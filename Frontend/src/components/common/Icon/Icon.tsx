import React, { FC, memo } from 'react';
import { BsHouseDoor, BsFillPersonFill, BsFillPhoneFill } from 'react-icons/bs';

export type SVGTypes = 'house' | 'person' | 'phone';

type IconProps = {
  name: SVGTypes;
  size?: number;
  className?: string;
};

const _Selector: { [key in SVGTypes]: FC<IconProps> } = {
  house: BsHouseDoor,
  person: BsFillPersonFill,
  phone: BsFillPhoneFill,
};

const Icon: FC<IconProps> = ({ name, ...props }) => {
  const IconComponent = _Selector[name];
  return <IconComponent name={name} {...props} />;
};

export default memo(Icon);
