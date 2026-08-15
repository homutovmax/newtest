<?php
header("Content-Type: text/html; charset=utf-8");

$raw_title = isset($_GET["title"]) ? $_GET["title"] : '';
$raw_company = isset($_GET["company"]) ? $_GET["company"] : '';
$raw_location = isset($_GET["location"]) ? $_GET["location"] : '';

$title = htmlspecialchars($raw_title ?: "Вакансия");
$company = htmlspecialchars($raw_company ?: "Компания");
$site = htmlspecialchars(isset($_GET["site"]) ? $_GET["site"] : "");
$siteId = htmlspecialchars(isset($_GET["id"]) ? $_GET["id"] : "");
$vacancyUrl = htmlspecialchars(isset($_GET["url"]) ? $_GET["url"] : "");
$salary = htmlspecialchars(isset($_GET["salary"]) ? $_GET["salary"] : "");
$location = htmlspecialchars($raw_location ?: "");
$v = isset($_GET["v"]) ? intval($_GET["v"]) : 0;

$resumeText = '';
$error = '';
$generated = false;

if ($v === 0 || $v === 5) {
    $tb64 = base64_encode($raw_title);
    $cb64 = $raw_company ? base64_encode($raw_company) : 'X3VuY25vd25f';
    $lb64 = $raw_location ? base64_encode($raw_location) : 'Xw';
    $script = __DIR__ . '/generate_resume_ai.py';
    $cmd = 'python3 ' . escapeshellarg($script) . ' ' . escapeshellarg($tb64) . ' ' . escapeshellarg($cb64) . ' ' . escapeshellarg($lb64) . ' 2>&1';
    $output = shell_exec($cmd);
    $data = json_decode($output, true);
    if ($data && isset($data['text'])) {
        $resumeText = $data['text'];
        $generated = true;
    } else {
        $errMsg = isset($data['error']) ? $data['error'] : ($output ? substr($output, 0, 200) : 'Нет ответа от генератора');
        $error = $errMsg;
    }
}
?>
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title><?=$generated ? 'Резюме для ' . $title : 'Генерация...'?> — AI Резюме</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Roboto, Arial, sans-serif;
    background: #f5f7fa;
    color: #1e293b;
    line-height: 1.6;
    padding: 20px;
  }
  .container { max-width: 800px; margin: 0 auto; }
  .card {
    background: #fff;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border: 1px solid #e2e8f0;
    margin-bottom: 20px;
  }
  .header {
    text-align: center;
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e2e8f0;
  }
  .header h1 { font-size: 22px; color: #2563eb; margin-bottom: 4px; }
  .header .meta { font-size: 14px; color: #64748b; }
  .resume-text {
    font-size: 14px;
    white-space: pre-wrap;
    line-height: 1.7;
    margin-bottom: 24px;
  }
  .actions {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #e2e8f0;
  }
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: all 0.15s;
  }
  .btn-primary { background: #0891b2; color: #fff; }
  .btn-primary:hover { background: #0e7490; }
  .btn-outline { background: #fff; color: #0891b2; border: 1px solid #0891b2; }
  .btn-outline:hover { background: #ecfeff; }
  .btn-success { background: #059669; color: #fff; }
  .btn-success:hover { background: #047857; }
  .toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #1e293b;
    color: #fff;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s;
    pointer-events: none;
    z-index: 100;
  }
  .toast.show { opacity: 1; transform: translateY(0); }
  .spinner {
    display: inline-block;
    width: 40px;
    height: 40px;
    border: 4px solid #e2e8f0;
    border-top-color: #2563eb;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 40px auto;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading-text { text-align: center; padding: 60px 0; }
  .loading-text p { color: #64748b; margin-top: 16px; font-size: 15px; }
  .error-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 16px;
    color: #991b1b;
    margin-bottom: 16px;
    text-align: center;
  }
  @media (max-width: 640px) { .card { padding: 20px; } .header h1 { font-size: 18px; } }
</style>
</head>
<body>
<div class="container">
  <div class="card">
    <div class="header">
      <h1>Резюме (AI)</h1>
      <div class="meta">Для: <?=$title?> · <?=$company?><?=$location ? ' · ' . $location : ''?></div>
    </div>

    <div class="variants">
      <a class="btn btn-outline" href="resume.php?id=<?=urlencode($siteId)?>&title=<?=urlencode($title)?>&company=<?=urlencode($company)?>&site=<?=urlencode($site)?>&url=<?=urlencode($vacancyUrl)?>">Открыть шаблонное резюме</a>
    </div>

    <?php if (!$generated && !$error): ?>
    <div class="loading-text" id="loading">
      <div class="spinner"></div>
      <p>Генерирую резюме с помощью DeepSeek AI...<br><small>Это может занять 10–20 секунд</small></p>
    </div>
    <?php endif; ?>

    <?php if ($error): ?>
    <div class="error-box">
      <p>❌ Не удалось сгенерировать резюме: <?=$error?></p>
      <p style="margin-top:8px">
        <a class="btn btn-outline" href="resume.php?id=<?=urlencode($siteId)?>&title=<?=urlencode($title)?>&company=<?=urlencode($company)?>&site=<?=urlencode($site)?>&url=<?=urlencode($vacancyUrl)?>">Открыть шаблонное резюме</a>
      </p>
    </div>
    <?php endif; ?>

    <?php if ($generated): ?>
    <div class="resume-text"><?=htmlspecialchars($resumeText)?></div>

    <div class="actions">
      <button class="btn btn-primary" onclick="copyResume()">📋 Копировать</button>
      <button class="btn btn-success" onclick="window.print()">🖨 Печать</button>
      <a class="btn btn-outline" href="vacancies_report.html">← Назад</a>
    </div>
    <?php endif; ?>
  </div>
</div>
<div class="toast" id="toast"></div>
<script>
function showToast(msg) {
  var t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(function() { t.classList.remove("show"); }, 3000);
}
function copyResume() {
  var text = document.querySelector('.resume-text').textContent;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function() {
      showToast('Скопировано!');
    }).catch(function() { fallbackCopy(text); });
  } else { fallbackCopy(text); }
}
function fallbackCopy(text) {
  var ta = document.createElement("textarea");
  ta.value = text; document.body.appendChild(ta);
  ta.select(); document.execCommand('copy');
  document.body.removeChild(ta); showToast('Скопировано!');
}
</script>
</body>
</html>
