export type UserRole = 'contractor' | 'curator' | 'operator';

export type RequestStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'REVIEW'
  | 'REVISION'
  | 'RESERVED'
  | 'ASSIGNED'
  | 'IN_PROGRESS'
  | 'STOCK_CHECK'
  | 'EDITED'
  | 'READY_FOR_EXPORT'
  | 'EXPORT_DONE'
  | 'IMPORT_PENDING'
  | 'IMPORTED'
  | 'IMPORT_ERROR'
  | 'CLOSED';

export interface User {
  id: string;
  name: string;
  role: UserRole;
}

export interface Material {
  id: string;
  name: string;
  oebsItemCode: string;
}

export interface RequestItem {
  id: string;
  materialId: string;
  materialName: string;
  requestedQty: number;
  comment?: string;
}

export interface EquipmentRequest {
  id: string;
  orgName: string;
  contactName: string;
  phone: string;
  email: string;
  aopNumber: string;
  status: RequestStatus;
  creatorId: string;
  creatorName: string;
  executorId?: string;
  executorName?: string;
  items: RequestItem[];
  createdAt: string;
  updatedAt: string;
}

export const STATUS_LABELS: Record<RequestStatus, string> = {
  DRAFT: 'Черновик',
  SUBMITTED: 'Отправлен',
  REVIEW: 'На проверке',
  REVISION: 'На доработке',
  RESERVED: 'Зарезервирован',
  ASSIGNED: 'Назначен',
  IN_PROGRESS: 'В работе',
  STOCK_CHECK: 'Проверка склада',
  EDITED: 'Изменён',
  READY_FOR_EXPORT: 'Готов к экспорту',
  EXPORT_DONE: 'Экспорт выполнен',
  IMPORT_PENDING: 'Ожидает импорта',
  IMPORTED: 'Импортирован',
  IMPORT_ERROR: 'Ошибка импорта',
  CLOSED: 'Закрыт',
};

export const STATUS_COLORS: Record<RequestStatus, string> = {
  DRAFT: 'default',
  SUBMITTED: 'processing',
  REVIEW: 'processing',
  REVISION: 'warning',
  RESERVED: 'success',
  ASSIGNED: 'blue',
  IN_PROGRESS: 'cyan',
  STOCK_CHECK: 'blue',
  EDITED: 'orange',
  READY_FOR_EXPORT: 'green',
  EXPORT_DONE: 'green',
  IMPORT_PENDING: 'processing',
  IMPORTED: 'success',
  IMPORT_ERROR: 'error',
  CLOSED: 'default',
};
