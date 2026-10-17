/**
 * WebSocket Streaming Client with automatic reconnection and message dispatch.
 */

export class RaceWebSocketClient {
  private ws: WebSocket | null = null;
  private raceId: string = '';
  private onMessageCallback: (data: any) => void;
  private reconnectTimeout: any = null;
  private isExplicitlyClosed: boolean = false;

  constructor(onMessage: (data: any) => void) {
    this.onMessageCallback = onMessage;
  }

  public connect(raceId: string): void {
    this.raceId = raceId;
    this.isExplicitlyClosed = false;

    if (this.ws) {
      this.ws.close();
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/races/${raceId}`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log(`WebSocket connected to race: ${raceId}`);
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onMessageCallback(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message', e);
        }
      };

      this.ws.onclose = () => {
        if (!this.isExplicitlyClosed) {
          this.reconnectTimeout = setTimeout(() => {
            this.connect(this.raceId);
          }, 2000);
        }
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket connection error:', err);
      };
    } catch (err) {
      console.warn('WebSocket init exception:', err);
    }
  }

  public send(action: string, value: any = null): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action, value }));
    }
  }

  public disconnect(): void {
    this.isExplicitlyClosed = true;
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
