import { useEffect, useRef, useState } from 'react';

const ACTUAL_WIDTH = 5; //meters
const ACTUAL_HEIGHT = 3; //meters
const WH_RATIO = ACTUAL_WIDTH / ACTUAL_HEIGHT;
const CANVAS_WIDTH = 1000;
const CANVAS_HEIGHT = CANVAS_WIDTH / WH_RATIO;
const PM_RATIO = CANVAS_WIDTH / ACTUAL_WIDTH;
const IMAGE_SIZE = 100;
const webSocketUrl = 'ws://127.0.0.1:8000/ws';

type Position = 'ld' | 'lu' | 'rd' | 'ru';

class Point {
  x: number;
  y: number;
  d: number;
  constructor(x: number, y: number, d: number) {
    this.x = x;
    this.y = y;
    this.d = d;
  }
}

class Triangulation {
  a: Point;
  b: Point;
  c: Point;
  constructor(a: Point, b: Point, c: Point) {
    this.a = a;
    this.b = b;
    this.c = c;
  }

  calc() {
    const A = 2 * (this.b.x - this.a.x);
    const B = 2 * (this.b.y - this.a.y);
    const C =
      this.a.d ** 2 -
      this.b.d ** 2 -
      this.a.x ** 2 +
      this.b.x ** 2 -
      this.a.y ** 2 +
      this.b.y ** 2;
    const D = 2 * (this.c.x - this.b.x);
    const E = 2 * (this.c.y - this.b.y);
    const F =
      this.b.d ** 2 -
      this.c.d ** 2 -
      this.b.x ** 2 +
      this.c.x ** 2 -
      this.b.y ** 2 +
      this.c.y ** 2;

    const x = (F * B - E * C) / (B * D - E * A);
    const y = (F * A - D * C) / (A * E - D * B);
    return new Point(x, y, 0);
  }
}

function canvasLenConverter(meter = 0) {
  return meter * PM_RATIO;
}

const HomePage = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // web socket
  const [socketConnected, setSocketConnected] = useState(false);
  const [sendMsg, setSendMsg] = useState(false);
  const [items, setItems] = useState([]);
  const ws = useRef<WebSocket | null>(null);
  //

  function canvasDrawArea(position: Position, radius = 0) {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.fillStyle = '#FF0000';
    ctx.globalAlpha = 0.3;
    ctx.beginPath();
    let x = -1;
    let y = -1;
    switch (position) {
      case 'ld':
        x = 0;
        y = CANVAS_HEIGHT;
        break;
      case 'lu':
        x = 0;
        y = 0;
        break;
      case 'rd':
        x = CANVAS_WIDTH;
        y = CANVAS_HEIGHT;
        break;
      case 'ru':
        x = CANVAS_WIDTH;
        y = 0;
        break;
    }
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();

    canvasDrawPhoneIcon(position);
  }

  function canvasDrawIcon(x = 0, y = 0, icon = '') {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.globalAlpha = 1;
    const img = new Image();
    img.onload = function () {
      ctx.drawImage(
        img,
        x - IMAGE_SIZE / 2,
        y - IMAGE_SIZE / 2,
        IMAGE_SIZE,
        IMAGE_SIZE,
      );
    };
    img.src =
      'https://fonts.gstatic.com/s/i/materialiconsoutlined/' +
      icon +
      '/v12/24px.svg';
  }
  function canvasDrawPhoneIcon(position = '') {
    let x = -1;
    let y = -1;
    switch (position) {
      case 'ld':
        x = IMAGE_SIZE / 2;
        y = CANVAS_HEIGHT - IMAGE_SIZE / 2;
        break;
      case 'lu':
        x = IMAGE_SIZE / 2;
        y = IMAGE_SIZE / 2;
        break;
      case 'rd':
        x = CANVAS_WIDTH - IMAGE_SIZE / 2;
        y = CANVAS_HEIGHT - IMAGE_SIZE / 2;
        break;
      case 'ru':
        x = CANVAS_WIDTH - IMAGE_SIZE;
        y = IMAGE_SIZE / 2;
        break;
    }
    canvasDrawIcon(x, y, 'phone_android');
  }

  const initCanvas = () => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    canvas.height = CANVAS_HEIGHT;
    canvas.width = CANVAS_WIDTH;
  };

  useEffect(() => {
    initCanvas();
    canvasDrawArea('lu', canvasLenConverter(2));
    canvasDrawArea('ld', canvasLenConverter(3.2));
    canvasDrawArea('ru', canvasLenConverter(3.3));
    const newTriangular = new Triangulation(
      new Point(0, 0, canvasLenConverter(2)),
      new Point(0, 600, canvasLenConverter(3.2)),
      new Point(1000, 0, canvasLenConverter(3.3)),
    );
    const calculatedPos = newTriangular.calc();
    canvasDrawIcon(calculatedPos.x, calculatedPos.y, 'account_circle');
  }, []);

  // 소켓 객체 생성
  useEffect(() => {
    if (!ws.current) {
      ws.current = new WebSocket(webSocketUrl);
      ws.current.onopen = () => {
        console.log('connected to ' + webSocketUrl);
        setSocketConnected(true);
      };
      ws.current.onclose = error => {
        console.log('disconnect from ' + webSocketUrl);
        console.log(error);
      };
      ws.current.onerror = error => {
        console.log('connection error ' + webSocketUrl);
        console.log(error);
      };
      ws.current.onmessage = evt => {
        const data = JSON.parse(evt.data);
        console.log(data);
      };
    }

    return () => {
      console.log('clean up');
      if (ws.current) ws.current.close();
    };
  }, []);

  // 소켓이 연결되었을 시에 send 메소드
  useEffect(() => {
    if (ws.current && socketConnected) {
      ws.current.send(
        JSON.stringify({
          message: sendMsg,
        }),
      );

      setSendMsg(true);
    }
  }, [socketConnected]);

  return (
    <div>
      <canvas ref={canvasRef} />
    </div>
  );
};

export default HomePage;
