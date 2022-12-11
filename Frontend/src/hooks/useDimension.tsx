import { RefObject, useRef, useState } from 'react';
import { useWindowResize } from '.';

export default function useDimension(delay: number): [
  RefObject<HTMLDivElement> | null,
  {
    width: number;
    height: number;
  },
] {
  const ref = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({
    width: 0,
    height: 0,
  });

  useWindowResize(() => {
    if (ref.current) {
      setDimensions({
        width: ref.current.clientWidth,
        height: ref.current.clientHeight,
      });
    }
  }, delay);

  return [ref, dimensions];
}
