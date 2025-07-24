import React, { useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { useNotificationStore } from '../../store/notificationStore';
import { Notification } from '../../types';

const slideIn = keyframes`
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

const slideOut = keyframes`
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
`;

const NotificationWrapper = styled.div`
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 400px;
  width: 100%;
  
  @media (max-width: 640px) {
    top: 1rem;
    left: 1rem;
    right: 1rem;
    max-width: none;
  }
`;

const NotificationItem = styled.div<{ 
  type: Notification['type']; 
  isExiting?: boolean 
}>`
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  position: relative;
  animation: ${({ isExiting }) => isExiting ? slideOut : slideIn} 0.3s ease-out;
  
  ${({ type }) => {
    switch (type) {
      case 'success':
        return `
          background-color: #f0fff4;
          border-left: 4px solid #48bb78;
          color: #2f855a;
        `;
      case 'error':
        return `
          background-color: #fed7d7;
          border-left: 4px solid #f56565;
          color: #c53030;
        `;
      case 'warning':
        return `
          background-color: #fefcbf;
          border-left: 4px solid #ed8936;
          color: #c05621;
        `;
      case 'info':
        return `
          background-color: #e6fffa;
          border-left: 4px solid #4299e1;
          color: #2b6cb0;
        `;
      default:
        return `
          background-color: #f7fafc;
          border-left: 4px solid #718096;
          color: #4a5568;
        `;
    }
  }}
`;

const NotificationIcon = styled.div<{ type: Notification['type'] }>`
  font-size: 1.25rem;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 0.125rem;
  
  ${({ type }) => {
    switch (type) {
      case 'success':
        return 'color: #48bb78;';
      case 'error':
        return 'color: #f56565;';
      case 'warning':
        return 'color: #ed8936;';
      case 'info':
        return 'color: #4299e1;';
      default:
        return 'color: #718096;';
    }
  }}
`;

const NotificationContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const NotificationTitle = styled.div`
  font-weight: 600;
  font-size: 0.875rem;
  line-height: 1.25;
  margin-bottom: 0.25rem;
`;

const NotificationMessage = styled.div`
  font-size: 0.8125rem;
  line-height: 1.4;
  opacity: 0.9;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  font-size: 1rem;
  line-height: 1;
  opacity: 0.7;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
  
  &:hover {
    opacity: 1;
  }
  
  &:focus {
    outline: 2px solid currentColor;
    outline-offset: 2px;
  }
`;

const ProgressBar = styled.div<{ duration: number; type: Notification['type'] }>`
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background-color: currentColor;
  opacity: 0.3;
  animation: progress ${({ duration }) => duration}ms linear;
  
  @keyframes progress {
    from {
      width: 100%;
    }
    to {
      width: 0%;
    }
  }
`;

const getIcon = (type: Notification['type']): string => {
  switch (type) {
    case 'success':
      return '✅';
    case 'error':
      return '❌';
    case 'warning':
      return '⚠️';
    case 'info':
      return 'ℹ️';
    default:
      return '📢';
  }
};

interface NotificationComponentProps {
  notification: Notification;
  onClose: (id: string) => void;
}

const NotificationComponent: React.FC<NotificationComponentProps> = ({
  notification,
  onClose,
}) => {
  const [isExiting, setIsExiting] = React.useState(false);

  useEffect(() => {
    if (notification.duration && notification.duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, notification.duration);

      return () => clearTimeout(timer);
    }
  }, [notification.duration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      onClose(notification.id);
    }, 300); // Match animation duration
  };

  return (
    <NotificationItem type={notification.type} isExiting={isExiting}>
      <NotificationIcon type={notification.type}>
        {getIcon(notification.type)}
      </NotificationIcon>
      
      <NotificationContent>
        <NotificationTitle>{notification.title}</NotificationTitle>
        {notification.message && (
          <NotificationMessage>{notification.message}</NotificationMessage>
        )}
      </NotificationContent>
      
      <CloseButton onClick={handleClose} title="Close notification">
        ×
      </CloseButton>
      
      {notification.duration && notification.duration > 0 && (
        <ProgressBar duration={notification.duration} type={notification.type} />
      )}
    </NotificationItem>
  );
};

const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useNotificationStore();

  if (notifications.length === 0) {
    return null;
  }

  return (
    <NotificationWrapper>
      {notifications.map((notification) => (
        <NotificationComponent
          key={notification.id}
          notification={notification}
          onClose={removeNotification}
        />
      ))}
    </NotificationWrapper>
  );
};

export default NotificationContainer; 