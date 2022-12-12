import React, { FC, useRef } from 'react';
import cx from 'classnames';

const PageLayout: FC<{
  children: React.ReactNode;
  fixedHeight?: boolean;
}> = ({ children, fixedHeight = false }) => {
  const mainRef = useRef<HTMLDivElement>(null);

  return (
    <div className="overflow-hidden w-full m-center">
      <div className="relative h-full">
        <main
          ref={mainRef}
          className={cx(
            'relative m-center w-full h-screen',
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
