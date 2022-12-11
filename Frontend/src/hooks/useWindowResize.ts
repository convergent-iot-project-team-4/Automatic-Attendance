import { useEffect } from 'react';
import { throttle } from 'lodash-es';

export default function useWindowResize(callback: () => void, delay: number) {
  useEffect(() => {
    const handleResize = throttle(() => {
      callback();
    }, delay);
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
}
