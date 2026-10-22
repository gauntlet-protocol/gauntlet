"""Host-side Unix socket to loopback HTTP relay for isolated fixture traffic.
Transport prototype only: no provider credentials and no remote access.
"""
import os,socket,threading

def relay_once(socket_path,target_port,ready):
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
  server.bind(str(socket_path));os.chmod(socket_path,0o600);server.listen(1);server.settimeout(10);ready.set()
  conn,_=server.accept()
  with conn,socket.create_connection(('127.0.0.1',target_port),timeout=5) as target:
   conn.settimeout(5);target.settimeout(5)
   def pump(source,dest):
    try:
     while True:
      chunk=source.recv(16384)
      if not chunk:break
      dest.sendall(chunk)
    except (OSError,TimeoutError):pass
    try:dest.shutdown(socket.SHUT_WR)
    except OSError:pass
   t=threading.Thread(target=pump,args=(conn,target),daemon=True);t.start();pump(target,conn);t.join(5)