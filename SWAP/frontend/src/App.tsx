import { useState, useMemo } from 'react';
import { ConfigProvider, Layout, Menu, Space, Tag, Typography, theme, Badge } from 'antd';
import {
  FormOutlined,
  DashboardOutlined,
  UserOutlined,
  SwapOutlined,
} from '@ant-design/icons';
import { store } from './store/mockData';
import { ContractorPage } from './pages/ContractorPage';
import { CuratorPage } from './pages/CuratorPage';
import { OperatorPage } from './pages/OperatorPage';
import type { UserRole } from './types';
import ruRU from 'antd/locale/ru_RU';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

const ROLE_LABELS: Record<UserRole, string> = {
  contractor: 'Подрядчик',
  curator: 'Куратор',
  operator: 'Оператор',
};

function App() {
  const [currentRole, setCurrentRole] = useState<UserRole>(store.getCurrentUser().role);
  const [selectedPage, setSelectedPage] = useState<string>('dashboard');
  const [collapsed, setCollapsed] = useState(false);

  const handleRoleChange = (role: UserRole) => {
    const user = store.getUsers().find(u => u.role === role);
    if (user) {
      store.setCurrentUser(user);
      setCurrentRole(role);
      setSelectedPage(role === 'contractor' ? 'create' : 'dashboard');
    }
  };

  const menuItems = useMemo(() => {
    if (currentRole === 'contractor') {
      return [
        { key: 'create', icon: <FormOutlined />, label: 'Создать запрос' },
        { key: 'my-requests', icon: <DashboardOutlined />, label: 'Мои запросы' },
      ];
    }
    if (currentRole === 'curator') {
      return [
        { key: 'dashboard', icon: <DashboardOutlined />, label: 'Панель управления' },
      ];
    }
    return [
      { key: 'queue', icon: <DashboardOutlined />, label: 'Моя очередь' },
    ];
  }, [currentRole]);

  const renderPage = () => {
    if (currentRole === 'contractor') {
      return <ContractorPage page={selectedPage} />;
    }
    if (currentRole === 'curator') {
      return <CuratorPage />;
    }
    return <OperatorPage />;
  };

  return (
    <ConfigProvider locale={ruRU} theme={{ algorithm: theme.defaultAlgorithm }}>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
          <div style={{ padding: '16px', textAlign: 'center' }}>
            <SwapOutlined style={{ fontSize: 28, color: '#1677ff' }} />
            {!collapsed && (
              <Title level={4} style={{ color: '#fff', margin: '8px 0 0', fontSize: 16 }}>
                SWAP Portal
              </Title>
            )}
          </div>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[selectedPage]}
            items={menuItems}
            onClick={({ key }) => setSelectedPage(key)}
          />
        </Sider>

        <Layout>
          <Header style={{ padding: '0 24px', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Space size="large">
              <Text strong style={{ fontSize: 16 }}>
                {ROLE_LABELS[currentRole]}
              </Text>
              <Tag color="blue">{store.getCurrentUser().name}</Tag>
            </Space>
            <Space>
              <Text type="secondary">Роль:</Text>
              {(['contractor', 'curator', 'operator'] as UserRole[]).map(role => (
                <Badge
                  key={role}
                  dot={currentRole === role}
                  offset={[-2, 2]}
                >
                  <Tag
                    color={currentRole === role ? 'blue' : 'default'}
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleRoleChange(role)}
                  >
                    <UserOutlined /> {ROLE_LABELS[role]}
                  </Tag>
                </Badge>
              ))}
            </Space>
          </Header>

          <Content style={{ margin: '24px', padding: 24, background: '#fff', borderRadius: 8, minHeight: 280 }}>
            {renderPage()}
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

export default App;
