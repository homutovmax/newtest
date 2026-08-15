<?php
header('Content-Type: text/plain; charset=utf-8');

$title = isset($_GET['title']) ? $_GET['title'] : '';
$company = isset($_GET['company']) ? $_GET['company'] : '';
$site = isset($_GET['site']) ? $_GET['site'] : '';
$siteId = isset($_GET['id']) ? $_GET['id'] : '';
$salary = isset($_GET['salary']) ? $_GET['salary'] : '';
$location = isset($_GET['location']) ? $_GET['location'] : '';
$url = isset($_GET['url']) ? $_GET['url'] : '';
$type = isset($_GET['type']) ? $_GET['type'] : 'both';
if (!$title) { echo "Error: no title\n"; exit; }

function b64e($s, $fb = 'Xw') { return $s ? base64_encode($s) : $fb; }
function genLetter($t, $c, $s, $l, $v) {
    $cmd = "python3 /home/m/maximum64/maximum64.beget.tech/public_html/generate_cover.py "
        . b64e($t) . " " . b64e($c, 'X3VuY25vd25f') . " $v " . b64e($s) . " " . b64e($l) . " 2>&1";
    $d = json_decode(shell_exec($cmd), true);
    return $d && isset($d['text']) ? $d['text'] : null;
}

$cd = $company ?: '(not specified)';
$msg = "📌 *$title*\n🏢 $cd";
if ($location) $msg .= "\n📍 $location";
if ($salary) $msg .= "\n💰 $salary";
$msg .= "\n🔗 [$site]($url) · ID: $siteId\n\n";

if ($type === 'cover' || $type === 'both') {
    $l = genLetter($title, $company, $salary, $location, 0);
    $msg .= $l ? "📝 *Cover Letter:*\n\n" . mb_substr($l, 0, 3500) : "❌ Generation failed";
    $msg .= "\n\n---\n\n";
}
if ($type === 'resume' || $type === 'both') {
    $p = http_build_query(['title'=>$title,'company'=>$company,'site'=>$site,'id'=>$siteId,'url'=>$url,'salary'=>$salary,'location'=>$location]);
    $msg .= "📄 *Resume:* 👉 http://maximum64.beget.tech/resume.php?$p\n\n";
}
$msg .= "⚡️ Say: «сформируй письмо для $title»";

// Write msg to temp file, pipe to Python script via stdin
$tmp = tempnam(sys_get_temp_dir(), 'tg');
file_put_contents($tmp, $msg);
$out = shell_exec("python3 /home/m/maximum64/maximum64.beget.tech/public_html/tg_send.py < " . escapeshellarg($tmp) . " 2>&1");
unlink($tmp);

if (trim($out) === 'True') {
    echo "✅ Sent to Telegram\n";
    exit;
}

// Fallback: PHP native
$data = array('chat_id' => '777125029', 'text' => $msg, 'parse_mode' => 'Markdown');
$opts = array('http' => array('method'=>'POST','header'=>'Content-Type: application/x-www-form-urlencoded','content'=>http_build_query($data),'timeout'=>30));
$r2 = @file_get_contents('https://api.telegram.org/botCHANGE_ME/sendMessage', false, stream_context_create($opts));
echo $r2 ? "✅ Sent via PHP\n" : "❌ Failed: $out\n";
