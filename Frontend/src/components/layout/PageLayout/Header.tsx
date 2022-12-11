import React, { FunctionComponent } from 'react';
import cx from 'classnames';

type Props = {
  className?: string;
  transparent?: boolean;
};

const Header: FunctionComponent<Props> = ({
  className,
  transparent = false,
}) => {
  return (
    <header className="relative">
      <div
        className={cx(
          'z-20 w-full max-w-mobile-app h-gb-header top-0',
          'px-side-padding py-2',
          'flex justify-between items-center align-middle',
          'font-bold',
          false ? 'fixed' : 'absolute',
          transparent && 'bg-transparent',
          className,
        )}
      >
        융합 iot 프로젝트
      </div>
    </header>
  );
};

export default Header;
