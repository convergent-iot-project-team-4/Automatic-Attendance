import React, { FC } from 'react';
import Icon, { SVGTypes } from './Icon';

interface IconButtonProps {
  classNames?: string;
  name: SVGTypes;
  type?: 'button' | 'submit' | 'reset';
  size?: number;
  onClick: (e?: unknown) => void;
}

const IconButton: FC<IconButtonProps> = ({
  classNames,
  type = 'button',
  onClick,
  ...props
}) => {
  return (
    <button type={type} onClick={onClick} className={classNames}>
      <Icon {...props} />
    </button>
  );
};

export default IconButton;
