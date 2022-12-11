import React, { FC, useRef } from 'react';
import cx from 'classnames';
import Header from './PageLayout/Header';

const PageLayout: FC<{
  children: React.ReactNode;
  fullWidth?: boolean;
  fixedHeight?: boolean;
  headerTransparent?: boolean;
  headerBackgroundColor?: string;
  headerContent?: React.ReactNode;
}> = ({
  children,
  fullWidth = false,
  fixedHeight = false,
  headerTransparent = false,
  headerBackgroundColor,
}) => {
  const mainRef = useRef<HTMLDivElement>(null);

  return (
    <div className="overflow-hidden w-full max-w-mobile-app m-center">
      <div className="relative h-full">
        <Header
          transparent={headerTransparent}
          className={headerBackgroundColor}
        />
        <main
          ref={mainRef}
          className={cx(
            'relative m-center w-full h-screen pt-gb-header pb-bt-nav',
            fullWidth ? null : `max-w-mobile-app px-side-padding`,
            fixedHeight ? 'overflow-hidden' : 'min-h-screen',
          )}
        >
          {children}
        </main>
      </div>
    </div>
  );
};

export default PageLayout;
