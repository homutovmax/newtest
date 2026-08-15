import { useState } from 'react';
import {
  Table,
  Tag,
  Button,
  Modal,
  Select,
  Space,
  Typography,
  Card,
  Row,
  Col,
  Statistic,
  message,
  Drawer,
  Descriptions,
  Timeline,
} from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  UserSwitchOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { store } from '../store/mockData';
import type { EquipmentRequest, RequestStatus } from '../types';
import { STATUS_LABELS, STATUS_COLORS } from '../types';

const { Title, Text } = Typography;

export function CuratorPage() {
  const [assignModalVisible, setAssignModalVisible] = useState(false);
  const [detailDrawer, setDetailDrawer] = useState<EquipmentRequest | null>(null);
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | undefined>(undefined);
  const [filterAop, setFilterAop] = useState('');

  const requests = store.getFilteredRequests({ status: filterStatus, aopNumber: filterAop });
  const operators = store.getUsers().filter(u => u.role === 'operator');

  const stats = store.getRequests();
  const totalRequests = stats.length;
  const submittedCount = stats.filter(r => r.status === 'SUBMITTED').length;
  const inProgressCount = stats.filter(r => ['IN_PROGRESS', 'ASSIGNED', 'STOCK_CHECK'].includes(r.status)).length;
  const closedCount = stats.filter(r => r.status === 'CLOSED').length;

  const handleAssign = (operatorId: string) => {
    if (selectedRequestId) {
      store.assignOperator(selectedRequestId, operatorId);
      message.success('Оператор назначен');
      setAssignModalVisible(false);
      setSelectedRequestId(null);
    }
  };

  const handleStatusChange = (id: string, status: RequestStatus) => {
    store.updateRequestStatus(id, status);
    message.success(`Статус изменён на "${STATUS_LABELS[status]}"`);
  };

  return (
    <div>
      <Title level={3}>Панель управления заявками</Title>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="Всего запросов" value={totalRequests} prefix={<ClockCircleOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="На review" value={submittedCount} valueStyle={{ color: '#1677ff' }} prefix={<ExclamationCircleOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="В работе" value={inProgressCount} valueStyle={{ color: '#52c41a' }} prefix={<CheckCircleOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Закрыто" value={closedCount} prefix={<CheckCircleOutlined />} /></Card>
        </Col>
      </Row>

      <Space style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="Фильтр по статусу"
          style={{ width: 200 }}
          onChange={(v) => setFilterStatus(v)}
          options={Object.entries(STATUS_LABELS).map(([k, v]) => ({ value: k, label: v }))}
        />
        <input
          placeholder="Поиск по AOP..."
          value={filterAop}
          onChange={(e) => setFilterAop(e.target.value)}
          style={{ padding: '4px 11px', borderRadius: 6, border: '1px solid #d9d9d9' }}
        />
      </Space>

      <Table
        dataSource={requests}
        rowKey="id"
        pagination={{ pageSize: 10 }}
        columns={[
          { title: 'Номер AOP', dataIndex: 'aopNumber', width: 160 },
          { title: 'Организация', dataIndex: 'orgName', width: 200 },
          {
            title: 'Статус',
            dataIndex: 'status',
            width: 180,
            render: (status: RequestStatus) => (
              <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</Tag>
            ),
          },
          { title: 'Создатель', dataIndex: 'creatorName', width: 150 },
          {
            title: 'Оператор',
            dataIndex: 'executorName',
            width: 150,
            render: (name: string) => name || <Text type="secondary">Не назначен</Text>,
          },
          {
            title: 'Действия',
            width: 250,
            render: (_, record) => (
              <Space size="small">
                <Button
                  size="small"
                  icon={<EyeOutlined />}
                  onClick={() => setDetailDrawer(record)}
                >
                  Детали
                </Button>
                {record.status !== 'CLOSED' && (
                  <Button
                    size="small"
                    type="primary"
                    icon={<UserSwitchOutlined />}
                    onClick={() => { setSelectedRequestId(record.id); setAssignModalVisible(true); }}
                  >
                    Назначить
                  </Button>
                )}
                {record.status === 'ASSIGNED' && (
                  <Button size="small" onClick={() => handleStatusChange(record.id, 'IN_PROGRESS')}>
                    В работу
                  </Button>
                )}
              </Space>
            ),
          },
        ]}
      />

      <Modal
        title="Назначить / Переназначить оператора"
        open={assignModalVisible}
        onCancel={() => setAssignModalVisible(false)}
        footer={null}
      >
        <Select
          style={{ width: '100%' }}
          placeholder="Выберите оператора"
          onChange={handleAssign}
          options={operators.map(o => ({ value: o.id, label: o.name }))}
        />
      </Modal>

      <Drawer
        title={`Запрос ${detailDrawer?.aopNumber}`}
        width={600}
        open={!!detailDrawer}
        onClose={() => setDetailDrawer(null)}
      >
        {detailDrawer && (
          <>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="Организация">{detailDrawer.orgName}</Descriptions.Item>
              <Descriptions.Item label="Контакт">{detailDrawer.contactName}</Descriptions.Item>
              <Descriptions.Item label="Телефон">{detailDrawer.phone}</Descriptions.Item>
              <Descriptions.Item label="Email">{detailDrawer.email}</Descriptions.Item>
              <Descriptions.Item label="Номер AOP">{detailDrawer.aopNumber}</Descriptions.Item>
              <Descriptions.Item label="Статус">
                <Tag color={STATUS_COLORS[detailDrawer.status]}>{STATUS_LABELS[detailDrawer.status]}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Оператор">{detailDrawer.executorName || 'Не назначен'}</Descriptions.Item>
              <Descriptions.Item label="Создан">{new Date(detailDrawer.createdAt).toLocaleString('ru-RU')}</Descriptions.Item>
            </Descriptions>

            <Title level={5} style={{ marginTop: 16 }}>Оборудование</Title>
            <Table
              dataSource={detailDrawer.items}
              rowKey="id"
              pagination={false}
              size="small"
              columns={[
                { title: 'Материал', dataIndex: 'materialName' },
                { title: 'Кол-во', dataIndex: 'requestedQty', width: 80 },
              ]}
            />

            <Title level={5} style={{ marginTop: 16 }}>История изменений</Title>
            <Timeline
              items={[
                { color: 'blue', children: `Запрос создан — ${new Date(detailDrawer.createdAt).toLocaleString('ru-RU')}` },
                { color: STATUS_COLORS[detailDrawer.status] === 'success' ? 'green' : 'gray', children: `Текущий статус: ${STATUS_LABELS[detailDrawer.status]}` },
              ]}
            />
          </>
        )}
      </Drawer>
    </div>
  );
}
