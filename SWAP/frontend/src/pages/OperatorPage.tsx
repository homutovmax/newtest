import { useState } from 'react';
import {
  Table,
  Tag,
  Button,
  Space,
  Typography,
  Card,
  Row,
  Col,
  Statistic,
  Modal,
  Select,
  InputNumber,
  message,
  Drawer,
  Descriptions,
  Progress,
  Popconfirm,
} from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  ExportOutlined,
  PlusOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { store } from '../store/mockData';
import type { EquipmentRequest, RequestItem, RequestStatus } from '../types';
import { STATUS_LABELS, STATUS_COLORS } from '../types';
import { v4 as uuidv4 } from 'uuid';

const { Title, Text } = Typography;

const MOCK_STOCK: Record<string, number> = {
  '1': 50, '2': 200, '3': 150, '4': 5, '5': 12, '6': 100, '7': 0, '8': 30,
};

export function OperatorPage() {
  const [detailDrawer, setDetailDrawer] = useState<EquipmentRequest | null>(null);
  const [editableItems, setEditableItems] = useState<RequestItem[]>([]);
  const [aopItems, setAopItems] = useState<RequestItem[]>([]);
  const [stockResults, setStockResults] = useState<Record<string, number>>({});
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [newMaterialId, setNewMaterialId] = useState<string | null>(null);
  const [newQty, setNewQty] = useState<number>(1);
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [excelGenerated, setExcelGenerated] = useState(false);

  const materials = store.getMaterials();
  const currentUser = store.getCurrentUser();
  const requests = store.getRequests().filter(
    r => r.executorId === currentUser.id && ['ASSIGNED', 'IN_PROGRESS', 'STOCK_CHECK', 'EDITED'].includes(r.status)
  );

  const assignedCount = requests.filter(r => r.status === 'ASSIGNED').length;
  const inProgressCount = requests.filter(r => r.status === 'IN_PROGRESS').length;

  const handleOpenRequest = (req: EquipmentRequest) => {
    if (req.status === 'ASSIGNED') {
      store.updateRequestStatus(req.id, 'IN_PROGRESS');
      message.info('Статус изменён на "В работе"');
    }
    const originalItems = req.items.map(i => ({ ...i }));
    setAopItems(originalItems);
    setEditableItems(req.items.map(i => ({ ...i })));
    setStockResults({});
    setDetailDrawer(req);
  };

  const handleCheckAllStock = () => {
    const results: Record<string, number> = {};
    editableItems.forEach(item => {
      results[item.materialId] = MOCK_STOCK[item.materialId] ?? 0;
    });
    setStockResults(results);
    message.success('Остатки по всем позициям проверены');
  };

  const handleCheckStock = (materialId: string) => {
    const qty = MOCK_STOCK[materialId] ?? 0;
    setStockResults(prev => ({ ...prev, [materialId]: qty }));
  };

  const handleQtyChange = (itemId: string, qty: number | null) => {
    setEditableItems(prev =>
      prev.map(i => i.id === itemId ? { ...i, requestedQty: qty || 1 } : i)
    );
  };

  const handleDeleteItem = (itemId: string) => {
    setEditableItems(prev => prev.filter(i => i.id !== itemId));
    setStockResults(prev => {
      const next = { ...prev };
      const item = editableItems.find(i => i.id === itemId);
      if (item) delete next[item.materialId];
      return next;
    });
  };

  const handleAddItem = () => {
    if (!newMaterialId) {
      message.warning('Выберите материал');
      return;
    }
    const mat = materials.find(m => m.id === newMaterialId);
    if (!mat) return;
    if (editableItems.some(i => i.materialId === mat.id)) {
      message.warning('Материал уже есть в списке');
      return;
    }
    const newItem: RequestItem = {
      id: uuidv4(),
      materialId: mat.id,
      materialName: mat.name,
      requestedQty: newQty,
    };
    setEditableItems(prev => [...prev, newItem]);
    setAddModalVisible(false);
    setNewMaterialId(null);
    setNewQty(1);
    message.success(`Добавлен: ${mat.name}`);
  };

  const handleSaveItems = () => {
    if (!detailDrawer) return;
    store.updateRequestItems(detailDrawer.id, editableItems);
    setDetailDrawer({ ...detailDrawer, items: editableItems });
    message.success('Список оборудования сохранён');
  };

  const handleMarkReady = (requestId: string) => {
    store.updateRequestStatus(requestId, 'READY_FOR_EXPORT');
    setDetailDrawer(prev => prev ? { ...prev, status: 'READY_FOR_EXPORT' } : null);
    setExcelGenerated(false);
    setExportModalVisible(true);
  };

  const handleGenerateExcel = () => {
    setExcelGenerated(true);
    message.success('Файл Excel сформирован и загружен в S3');
  };

  const handleSendToOEBS = () => {
    if (!detailDrawer) return;
    store.updateRequestStatus(detailDrawer.id, 'CLOSED');
    message.success('Заявка отправлена в OEBS и закрыта');
    setExportModalVisible(false);
    setDetailDrawer(null);
  };

  const getStockColor = (materialId: string, requestedQty: number) => {
    const qty = stockResults[materialId];
    if (qty === undefined) return undefined;
    if (qty === 0) return 'red';
    if (qty >= requestedQty) return 'green';
    return 'orange';
  };

  const getStockPercent = (materialId: string, requestedQty: number) => {
    const qty = stockResults[materialId];
    if (qty === undefined) return 0;
    return Math.min(100, Math.round((qty / requestedQty) * 100));
  };

  const usedMaterialIds = editableItems.map(i => i.materialId);
  const availableMaterials = materials.filter(m => !usedMaterialIds.includes(m.id));

  return (
    <div>
      <Title level={3}>Моя очередь заявок</Title>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card><Statistic title="Назначено" value={assignedCount} valueStyle={{ color: '#faad14' }} prefix={<ClockCircleOutlined />} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="В работе" value={inProgressCount} valueStyle={{ color: '#1677ff' }} prefix={<CheckCircleOutlined />} /></Card>
        </Col>
        <Col span={8}>
          <Card><Statistic title="Всего в очереди" value={requests.length} prefix={<ReloadOutlined />} /></Card>
        </Col>
      </Row>

      <Table
        dataSource={requests}
        rowKey="id"
        columns={[
          { title: 'Номер AOP', dataIndex: 'aopNumber', width: 160 },
          { title: 'Организация', dataIndex: 'orgName' },
          {
            title: 'Статус',
            dataIndex: 'status',
            width: 180,
            render: (status: RequestStatus) => (
              <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</Tag>
            ),
          },
          {
            title: 'Позиций',
            dataIndex: 'items',
            width: 80,
            render: (items: EquipmentRequest['items']) => items.length,
          },
          {
            title: 'Действия',
            width: 200,
            render: (_, record) => (
              <Button type="primary" onClick={() => handleOpenRequest(record)}>
                Открыть
              </Button>
            ),
          },
        ]}
      />

      <Drawer
        title={`Обработка: ${detailDrawer?.aopNumber}`}
        width={900}
        open={!!detailDrawer}
        onClose={() => setDetailDrawer(null)}
      >
        {detailDrawer && (
          <>
            <Descriptions column={2} bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Организация">{detailDrawer.orgName}</Descriptions.Item>
              <Descriptions.Item label="Контакт">{detailDrawer.contactName}</Descriptions.Item>
              <Descriptions.Item label="Статус">
                <Tag color={STATUS_COLORS[detailDrawer.status]}>{STATUS_LABELS[detailDrawer.status]}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Оператор">{detailDrawer.executorName}</Descriptions.Item>
            </Descriptions>

            <Space style={{ marginBottom: 12 }}>
              <Title level={5} style={{ margin: 0 }}>Оборудование</Title>
              <Button size="small" icon={<ReloadOutlined />} onClick={handleCheckAllStock}>
                Проверить всё (WMS)
              </Button>
              <Button size="small" type="primary" icon={<PlusOutlined />} onClick={() => setAddModalVisible(true)}>
                Добавить позицию
              </Button>
              <Popconfirm title="Сохранить изменения?" onConfirm={handleSaveItems} okText="Да" cancelText="Нет">
                <Button size="small">Сохранить</Button>
              </Popconfirm>
            </Space>

            <Table
              dataSource={editableItems}
              rowKey="id"
              pagination={false}
              size="small"
              rowClassName={(record) => {
                const isAop = aopItems.some(a => a.materialId === record.materialId);
                return isAop ? 'row-aop-item' : 'row-added-item';
              }}
              columns={[
                {
                  title: 'Источник',
                  width: 90,
                  render: (_, record) => {
                    const aopItem = aopItems.find(a => a.materialId === record.materialId);
                    if (aopItem) {
                      return <Tag color="blue">AOP</Tag>;
                    }
                    return <Tag color="green">Добавлен</Tag>;
                  },
                },
                {
                  title: 'Материал',
                  dataIndex: 'materialName',
                  width: 200,
                  render: (name: string, record) => (
                    <Space size={4}>
                      <Text>{name}</Text>
                      <Text type="secondary" style={{ fontSize: 11 }}>({materials.find(m => m.id === record.materialId)?.oebsItemCode})</Text>
                    </Space>
                  ),
                },
                {
                  title: 'Кол-во в AOP',
                  width: 90,
                  render: (_, record) => {
                    const aopItem = aopItems.find(a => a.materialId === record.materialId);
                    if (!aopItem) return <Text type="secondary">—</Text>;
                    const changed = aopItem.requestedQty !== record.requestedQty;
                    return (
                      <Text type={changed ? 'warning' : undefined} strong={changed}>
                        {aopItem.requestedQty}
                      </Text>
                    );
                  },
                },
                {
                  title: 'Текущее кол-во',
                  dataIndex: 'requestedQty',
                  width: 110,
                  render: (qty: number, record) => {
                    const aopItem = aopItems.find(a => a.materialId === record.materialId);
                    const isChanged = aopItem && aopItem.requestedQty !== qty;
                    return (
                      <InputNumber
                        min={1}
                        size="small"
                        value={qty}
                        onChange={(v) => handleQtyChange(record.id, v)}
                        style={{ width: 75, borderColor: isChanged ? '#faad14' : undefined }}
                      />
                    );
                  },
                },
                {
                  title: 'Остаток (WMS)',
                  width: 210,
                  render: (_, record) => {
                    const qty = stockResults[record.materialId];
                    if (qty === undefined) {
                      return (
                        <Button size="small" icon={<ReloadOutlined />} onClick={() => handleCheckStock(record.materialId)}>
                          Проверить
                        </Button>
                      );
                    }
                    const color = getStockColor(record.materialId, record.requestedQty);
                    return (
                      <Space size={4}>
                        <Progress
                          percent={getStockPercent(record.materialId, record.requestedQty)}
                          size="small"
                          status={qty === 0 ? 'exception' : color === 'green' ? 'success' : 'active'}
                          style={{ width: 70 }}
                        />
                        <Tag color={color}>{qty}</Tag>
                        {qty === 0 && <Text type="danger" style={{ fontSize: 11 }}>нет!</Text>}
                        {qty > 0 && qty < record.requestedQty && <Text type="warning" style={{ fontSize: 11 }}>мало</Text>}
                      </Space>
                    );
                  },
                },
                {
                  title: '',
                  width: 40,
                  render: (_, record) => (
                    <Popconfirm title="Удалить позицию?" onConfirm={() => handleDeleteItem(record.id)} okText="Да" cancelText="Нет">
                      <Button danger type="text" size="small" icon={<DeleteOutlined />} />
                    </Popconfirm>
                  ),
                },
              ]}
            />

            {editableItems.length > 0 && (
              <Space style={{ marginTop: 16 }}>
                {detailDrawer.status === 'IN_PROGRESS' && (
                  <Button type="primary" icon={<ExportOutlined />} onClick={() => handleMarkReady(detailDrawer.id)}>
                    Готов к экспорту
                  </Button>
                )}
              </Space>
            )}
          </>
        )}
      </Drawer>

      <Modal
        title="Добавить позицию"
        open={addModalVisible}
        onCancel={() => { setAddModalVisible(false); setNewMaterialId(null); setNewQty(1); }}
        onOk={handleAddItem}
        okText="Добавить"
        cancelText="Отмена"
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text>Материал:</Text>
          <Select
            showSearch
            style={{ width: '100%' }}
            placeholder="Выберите материал из каталога"
            value={newMaterialId}
            onChange={setNewMaterialId}
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={availableMaterials.map(m => ({
              value: m.id,
              label: `${m.name} (${m.oebsItemCode})`,
            }))}
          />
          <Text>Количество:</Text>
          <InputNumber min={1} value={newQty} onChange={(v) => setNewQty(v || 1)} style={{ width: '100%' }} />
        </Space>
      </Modal>

      <Modal
        title="Экспорт и отправка в OEBS"
        open={exportModalVisible}
        onCancel={() => setExportModalVisible(false)}
        footer={null}
        width={600}
      >
        {detailDrawer && (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="Заявка">{detailDrawer.aopNumber}</Descriptions.Item>
              <Descriptions.Item label="Организация">{detailDrawer.orgName}</Descriptions.Item>
              <Descriptions.Item label="Позиций">{editableItems.length}</Descriptions.Item>
            </Descriptions>

            <Table
              dataSource={editableItems}
              rowKey="id"
              pagination={false}
              size="small"
              columns={[
                { title: 'Материал', dataIndex: 'materialName' },
                { title: 'Кол-во', dataIndex: 'requestedQty', width: 80 },
              ]}
            />

            <Space direction="vertical" style={{ width: '100%' }}>
              {!excelGenerated ? (
                <Button
                  type="primary"
                  icon={<ExportOutlined />}
                  block
                  size="large"
                  onClick={handleGenerateExcel}
                >
                  Сгенерировать файл для выгрузки
                </Button>
              ) : (
                <>
                  <div style={{ background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: 6, padding: '12px 16px', marginBottom: 8 }}>
                    <Space>
                      <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 16 }} />
                      <Text>Файл Excel успешно сформирован</Text>
                    </Space>
                  </div>
                  <Popconfirm
                    title="Отправить заявку в OEBS?"
                    description="После отправки заявка будет закрыта"
                    onConfirm={handleSendToOEBS}
                    okText="Да, отправить"
                    cancelText="Отмена"
                    okButtonProps={{ danger: true }}
                  >
                    <Button
                      type="primary"
                      danger
                      block
                      size="large"
                    >
                      Отправить в списание (OEBS)
                    </Button>
                  </Popconfirm>
                </>
              )}
            </Space>
          </Space>
        )}
      </Modal>
    </div>
  );
}
