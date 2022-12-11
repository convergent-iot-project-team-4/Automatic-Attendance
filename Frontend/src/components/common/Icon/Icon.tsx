import React, { FC, memo } from 'react';
import {
  BsApple,
  BsCamera,
  BsGoogle,
  BsHouseDoor,
  BsPlus,
} from 'react-icons/bs';
import { AiOutlinePlusCircle } from 'react-icons/ai';
import { CgProfile } from 'react-icons/cg';
import { IoIosArrowBack, IoIosArrowForward } from 'react-icons/io';
import { IoAlbumsOutline, IoEllipsisVertical } from 'react-icons/io5';
import { RiKakaoTalkFill } from 'react-icons/ri';
import { FaSearch } from 'react-icons/fa';
import { BiVideo } from 'react-icons/bi';
import { GiHamburgerMenu } from 'react-icons/gi';

export type SVGTypes =
  | 'house'
  | 'plus'
  | 'plusCircle'
  | 'profile'
  | 'album'
  | 'camera'
  | 'video'
  | 'hamburger'
  | 'search'
  | 'leftArrow'
  | 'rightArrow'
  | 'ellipsisVertical'
  | 'google'
  | 'apple'
  | 'kakao';

type IconProps = {
  name: SVGTypes;
  size?: number;
  className?: string;
};

const _Selector: { [key in SVGTypes]: FC<IconProps> } = {
  house: BsHouseDoor,
  plus: BsPlus,
  plusCircle: AiOutlinePlusCircle,
  profile: CgProfile,
  album: IoAlbumsOutline,
  camera: BsCamera,
  video: BiVideo,
  hamburger: GiHamburgerMenu,
  search: FaSearch,
  leftArrow: IoIosArrowBack,
  rightArrow: IoIosArrowForward,
  ellipsisVertical: IoEllipsisVertical,
  google: BsGoogle,
  apple: BsApple,
  kakao: RiKakaoTalkFill,
};

const Icon: FC<IconProps> = ({ name, ...props }) => {
  const IconComponent = _Selector[name];
  return <IconComponent name={name} {...props} />;
};

export default memo(Icon);
