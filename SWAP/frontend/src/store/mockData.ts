import type { EquipmentRequest, User, Material } from '../types';
import { v4 as uuidv4 } from 'uuid';

const MATERIALS: Material[] = [
  { id: '1', name: 'Кабель Cat6 UTP 305м', oebsItemCode: 'CBL-CAT6-305' },
  { id: '2', name: 'Розетка RJ-45 Cat6', oebsItemCode: 'RJ45-CAT6' },
  { id: '3', name: 'Патч-корд 2м Cat6', oebsItemCode: 'PATCH-2M-CAT6' },
  { id: '4', name: 'Коммутатор 24-порт', oebsItemCode: 'SW-24P' },
  { id: '5', name: 'Кроссовая панель 24-порт', oebsItemCode: 'PATCH-24P' },
  { id: '6', name: 'Кабель-канал 40x25мм', oebsItemCode: 'CABLE-DUCT-40' },
  { id: '7', name: 'Хаб 8-портовый', oebsItemCode: 'HUB-8P' },
  { id: '8', name: 'Адаптер USB-Ethernet', oebsItemCode: 'USB-ETH' },
];

const USERS: User[] = [
  { id: 'u1', name: 'Иванов И.И.', role: 'contractor' },
  { id: 'u2', name: 'Петрова А.В.', role: 'curator' },
  { id: 'u3', name: 'Сидоров К.М.', role: 'operator' },
  { id: 'u4', name: 'Козлова Е.П.', role: 'operator' },
];

const now = new Date().toISOString();

let requests: EquipmentRequest[] = [
  {
    id: uuidv4(),
    orgName: 'ООО "СтройМонтаж"',
    contactName: 'Иванов И.И.',
    phone: '+7 (495) 123-45-67',
    email: 'ivanov@stroy.com',
    aopNumber: 'AOP-2026-001',
    status: 'RESERVED',
    creatorId: 'u1',
    creatorName: 'Иванов И.И.',
    executorId: 'u3',
    executorName: 'Сидоров К.М.',
    items: [
      { id: uuidv4(), materialId: '1', materialName: 'Кабель Cat6 UTP 305м', requestedQty: 5 },
      { id: uuidv4(), materialId: '2', materialName: 'Розетка RJ-45 Cat6', requestedQty: 40 },
    ],
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    updatedAt: now,
  },
  {
    id: uuidv4(),
    orgName: 'АО "ТелекомСервис"',
    contactName: 'Петров П.П.',
    phone: '+7 (495) 987-65-43',
    email: 'petrov@telecom.ru',
    aopNumber: 'AOP-2026-002',
    status: 'SUBMITTED',
    creatorId: 'u1',
    creatorName: 'Иванов И.И.',
    items: [
      { id: uuidv4(), materialId: '4', materialName: 'Коммутатор 24-порт', requestedQty: 3 },
      { id: uuidv4(), materialId: '3', materialName: 'Патч-корд 2м Cat6', requestedQty: 72 },
    ],
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: now,
  },
  {
    id: uuidv4(),
    orgName: 'ООО "ИнфоСеть"',
    contactName: 'Сидоров С.С.',
    phone: '+7 (495) 555-12-34',
    email: 'sidorov@info.net',
    aopNumber: 'AOP-2026-003',
    status: 'IN_PROGRESS',
    creatorId: 'u1',
    creatorName: 'Иванов И.И.',
    executorId: 'u4',
    executorName: 'Козлова Е.П.',
    items: [
      { id: uuidv4(), materialId: '5', materialName: 'Кроссовая панель 24-порт', requestedQty: 10 },
      { id: uuidv4(), materialId: '6', materialName: 'Кабель-канал 40x25мм', requestedQty: 20 },
    ],
    createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
    updatedAt: now,
  },
  {
    id: uuidv4(),
    orgName: 'ПАО "СвязьИнвест"',
    contactName: 'Козлова К.К.',
    phone: '+7 (495) 222-33-44',
    email: 'kozlova@svyaz.ru',
    aopNumber: 'AOP-2026-004',
    status: 'REVISION',
    creatorId: 'u1',
    creatorName: 'Иванов И.И.',
    items: [
      { id: uuidv4(), materialId: '7', materialName: 'Хаб 8-портовый', requestedQty: 15 },
      { id: uuidv4(), materialId: '8', materialName: 'Адаптер USB-Ethernet', requestedQty: 30 },
    ],
    createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
    updatedAt: now,
  },
];

let currentUser: User = USERS[0]; // По умолчанию — Подрядчик

export const store = {
  getMaterials: () => MATERIALS,
  getUsers: () => USERS,
  getCurrentUser: () => currentUser,
  setCurrentUser: (user: User) => { currentUser = user; },

  getRequests: () => [...requests],

  getFilteredRequests: (filters: { status?: string; aopNumber?: string }) => {
    let result = [...requests];
    if (currentUser.role === 'contractor') {
      result = result.filter(r => r.creatorId === currentUser.id);
    }
    if (filters.status) {
      result = result.filter(r => r.status === filters.status);
    }
    if (filters.aopNumber && filters.aopNumber.length > 0) {
      result = result.filter(r => r.aopNumber.toLowerCase().includes(filters.aopNumber!.toLowerCase()));
    }
    return result;
  },

  createRequest: (data: {
    orgName: string;
    contactName: string;
    phone: string;
    email: string;
    aopNumber: string;
    items: { materialId: string; materialName: string; requestedQty: number }[];
  }): EquipmentRequest => {
    const newRequest: EquipmentRequest = {
      id: uuidv4(),
      ...data,
      status: 'DRAFT',
      creatorId: currentUser.id,
      creatorName: currentUser.name,
      items: data.items.map(item => ({ ...item, id: uuidv4() })),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    requests = [newRequest, ...requests];
    return newRequest;
  },

  submitRequest: (id: string) => {
    requests = requests.map(r =>
      r.id === id ? { ...r, status: 'SUBMITTED' as const, updatedAt: new Date().toISOString() } : r
    );
  },

  updateRequestStatus: (id: string, status: EquipmentRequest['status']) => {
    requests = requests.map(r =>
      r.id === id ? { ...r, status, updatedAt: new Date().toISOString() } : r
    );
  },

  assignOperator: (requestId: string, operatorId: string) => {
    const operator = USERS.find(u => u.id === operatorId);
    requests = requests.map(r =>
      r.id === requestId
        ? { ...r, executorId: operatorId, executorName: operator?.name, status: 'ASSIGNED' as const, updatedAt: new Date().toISOString() }
        : r
    );
  },

  updateRequestItems: (requestId: string, items: EquipmentRequest['items']) => {
    requests = requests.map(r =>
      r.id === requestId
        ? { ...r, items, updatedAt: new Date().toISOString() }
        : r
    );
  },
};
