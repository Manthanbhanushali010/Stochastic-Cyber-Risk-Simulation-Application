import { create } from 'zustand';
import { Notification } from '../types';

interface NotificationStore {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  showSuccess: (title: string, message?: string, duration?: number) => void;
  showError: (title: string, message?: string, duration?: number) => void;
  showWarning: (title: string, message?: string, duration?: number) => void;
  showInfo: (title: string, message?: string, duration?: number) => void;
}

const generateId = () => Math.random().toString(36).substr(2, 9);

export const useNotificationStore = create<NotificationStore>((set, get) => ({
  notifications: [],

  addNotification: (notificationData) => {
    const notification: Notification = {
      id: generateId(),
      timestamp: new Date().toISOString(),
      duration: notificationData.duration || 5000, // Default 5 seconds
      ...notificationData,
    };

    set((state) => ({
      notifications: [...state.notifications, notification],
    }));

    // Auto-remove notification after duration (if specified)
    if (notification.duration && notification.duration > 0) {
      setTimeout(() => {
        get().removeNotification(notification.id);
      }, notification.duration);
    }
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter(n => n.id !== id),
    }));
  },

  clearAllNotifications: () => {
    set({ notifications: [] });
  },

  showSuccess: (title, message, duration = 4000) => {
    get().addNotification({
      type: 'success',
      title,
      message,
      duration,
    });
  },

  showError: (title, message, duration = 6000) => {
    get().addNotification({
      type: 'error',
      title,
      message,
      duration,
    });
  },

  showWarning: (title, message, duration = 5000) => {
    get().addNotification({
      type: 'warning',
      title,
      message,
      duration,
    });
  },

  showInfo: (title, message, duration = 4000) => {
    get().addNotification({
      type: 'info',
      title,
      message,
      duration,
    });
  },
})); 