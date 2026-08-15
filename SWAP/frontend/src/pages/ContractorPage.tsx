import { useState } from 'react';
import {
  Form,
  Input,
  InputNumber,
  Table,
  Button,
  Space,
  Select,
  message,
  Card,
  Typography,
  Popconfirm,
  Tag,
  Steps,
} from 'antd';
import { DeleteOutlined, SendOutlined, SaveOutlined } from '@ant-design/icons';
import { store } from '../store/mockData';
import type { EquipmentRequest } from '../types';
import { STATUS_LABELS, STATUS_COLORS } from '../types';
import { v4 as uuidv4 } from 'uuid';

const { Title, Text } = Typography;

interface RequestFormValues {
  orgName: string;
  contactName: string;
  phone: string;
  email: string;
  aopNumber: string;
}

interface FormItem {
  key: string;
  materialId: string;
  materialName: string;
  requestedQty: number;
  comment?: string;
}

export function ContractorPage({ page }: { page: string }) {
  if (page === 'my-requests') return <MyRequests />;
  return <CreateRequest />;
}

function CreateRequest() {
  const [form] = Form.useForm<RequestFormValues>();
  const [currentStep, setCurrentStep] = useState(0);
  const [items, setItems] = useState<FormItem[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<string | null>(null);
  const materials = store.getMaterials();

  const handleAddMaterial = () => {
    if (!selectedMaterial) {
      message.warning('Выберите материал');
      return;
    }
    const mat = materials.find(m => m.id === selectedMaterial);
    if (!mat) return;
    if (items.some(i => i.materialId === mat.id)) {
      message.warning('Материал уже добавлен');
      return;
    }
    setItems([...items, {
      key: uuidv4(),
      materialId: mat.id,
      materialName: mat.name,
      requestedQty: 1,
    }]);
    setSelectedMaterial(null);
  };

  const handleRemoveItem = (key: string) => {
    setItems(items.filter(i => i.key !== key));
  };

  const handleQtyChange = (key: string, qty: number | null) => {
    setItems(items.map(i => i.key === key ? { ...i, requestedQty: qty || 1 } : i));
  };

  const handleSubmit = (status: 'DRAFT' | 'SUBMITTED') => {
    form.validateFields().then(values => {
      if (items.length === 0) {
        message.error('Добавьте хотя бы один материал');
        return;
      }
      store.createRequest({
        ...values,
        items: items.map(i => ({
          materialId: i.materialId,
          materialName: i.materialName,
          requestedQty: i.requestedQty,
        })),
      });
      if (status === 'SUBMITTED') {
        const all = store.getRequests();
        store.submitRequest(all[0].id);
      }
      message.success(status === 'DRAFT' ? 'Черновик сохранён' : 'Запрос отправлен на.review');
      form.resetFields();
      setItems([]);
      setCurrentStep(0);
    });
  };

  return (
    <div>
      <Title level={3}>Создать запрос оборудования</Title>

      <Steps
        current={currentStep}
        style={{ marginBottom: 32 }}
        items={[
          { title: 'Контактные данные' },
          { title: 'Оборудование' },
          { title: 'Подтверждение' },
        ]}
      />

      {currentStep === 0 && (
        <Form form={form} layout="vertical" style={{ maxWidth: 600 }}>
          <Form.Item name="orgName" label="Организация" rules={[{ required: true, message: 'Обязательное поле' }]}>
            <Input placeholder="Название организации" />
          </Form.Item>
          <Form.Item name="contactName" label="Контактное лицо (ФИО)" rules={[{ required: true }]}>
            <Input placeholder="Иванов Иван Иванович" />
          </Form.Item>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <Form.Item name="phone" label="Телефон" rules={[{ required: true }]}>
              <Input placeholder="+7 (___) ___-__-__" />
            </Form.Item>
            <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
              <Input placeholder="email@company.com" />
            </Form.Item>
          </div>
          <Form.Item name="aopNumber" label="Номер AOP" rules={[{ required: true }]}>
            <Input placeholder="AOP-2026-XXX" />
          </Form.Item>
          <Button type="primary" onClick={() => {
            form.validateFields().then(() => setCurrentStep(1)).catch(() => {});
          }}>
            Далее
          </Button>
        </Form>
      )}

      {currentStep === 1 && (
        <div>
          <Space style={{ marginBottom: 16 }}>
            <Select
              showSearch
              style={{ width: 300 }}
              placeholder="Выберите материал"
              value={selectedMaterial}
              onChange={setSelectedMaterial}
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={materials.map(m => ({ value: m.id, label: `${m.name} (${m.oebsItemCode})` }))}
            />
            <Button onClick={handleAddMaterial}>+ Добавить</Button>
          </Space>

          <Table
            dataSource={items}
            rowKey="key"
            pagination={false}
            columns={[
              { title: 'Материал', dataIndex: 'materialName' },
              {
                title: 'Количество',
                dataIndex: 'requestedQty',
                width: 120,
                render: (_, record) => (
                  <InputNumber min={1} value={record.requestedQty} onChange={(v) => handleQtyChange(record.key, v)} />
                ),
              },
              {
                title: '',
                width: 50,
                render: (_, record) => (
                  <Button danger type="text" icon={<DeleteOutlined />} onClick={() => handleRemoveItem(record.key)} />
                ),
              },
            ]}
          />

          <Space style={{ marginTop: 16 }}>
            <Button onClick={() => setCurrentStep(0)}>Назад</Button>
            <Button type="primary" onClick={() => setCurrentStep(2)} disabled={items.length === 0}>
              Далее
            </Button>
          </Space>
        </div>
      )}

      {currentStep === 2 && (
        <div>
          <Card title="Проверьте данные" style={{ maxWidth: 600, marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text><strong>Организация:</strong> {form.getFieldValue('orgName')}</Text>
              <Text><strong>Контакт:</strong> {form.getFieldValue('contactName')}</Text>
              <Text><strong>AOP:</strong> {form.getFieldValue('aopNumber')}</Text>
              <Text><strong>Позиций:</strong> {items.length}</Text>
              {items.map(item => (
                <Tag key={item.key}>{item.materialName} x{item.requestedQty}</Tag>
              ))}
            </Space>
          </Card>

          <Space>
            <Button onClick={() => setCurrentStep(1)}>Назад</Button>
            <Popconfirm title="Сохранить как черновик?" onConfirm={() => handleSubmit('DRAFT')} okText="Да" cancelText="Нет">
              <Button icon={<SaveOutlined />}>Черновик</Button>
            </Popconfirm>
            <Button type="primary" icon={<SendOutlined />} onClick={() => handleSubmit('SUBMITTED')}>
              Отправить на review
            </Button>
          </Space>
        </div>
      )}
    </div>
  );
}

function MyRequests() {
  const requests = store.getFilteredRequests({});

  return (
    <div>
      <Title level={3}>Мои запросы</Title>
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
            render: (status: EquipmentRequest['status']) => (
              <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</Tag>
            ),
          },
          {
            title: 'Позиций',
            dataIndex: 'items',
            width: 80,
            render: (items: EquipmentRequest['items']) => items.length,
          },
          { title: 'Создан', dataIndex: 'createdAt', width: 180, render: (v: string) => new Date(v).toLocaleDateString('ru-RU') },
        ]}
      />
    </div>
  );
}
