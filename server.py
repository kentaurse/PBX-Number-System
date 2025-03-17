import socket
import json
import threading
import logging
from Phones import Scraper

# ログの設定
logging.basicConfig(filename='server.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 設定
HOST = '127.0.0.1'  # ローカルホストに変更
PORT = 12345      # 権限問題の少ない高いポート番号
URL = 'http://10.183.9.58'  # 実際の接続時に変更
USER_ID = '10'
PASSWORD = '0000'

# テスト用のダミーデータ
DUMMY_RECORDS = [
    {'index': '1', 'date': '2023/06/01 10:30', 'caller': '03-1234-5678', 'duration': '00:45', 'status': '未読'},
    {'index': '2', 'date': '2023/06/02 14:15', 'caller': '090-1234-5678', 'duration': '01:20', 'status': '既読'}
]

def handle_client(client_socket):
    """クライアント接続を処理する関数"""
    try:
        # クライアントからのリクエストを受信
        request = client_socket.recv(1024).decode('utf-8')
        logging.info(f"リクエスト受信: {request}")
        print(f"リクエスト受信: {request}")
        
        if request == "get_voicemail":
            try:
                # テスト用：実際のScraperの代わりにダミーデータを使用
                print("テストモード: ダミーデータを返します")
                records = DUMMY_RECORDS
                
                # 本番環境では以下のコードを使用
                # asr = Scraper(URL, USER_ID, PASSWORD)
                # asr.go_to_voicemail()
                # records = asr.get_recent_records()
                # asr.end_session()
                
                # JSONに変換して送信
                response = json.dumps(records, ensure_ascii=False)
                client_socket.send(response.encode('utf-8'))
                logging.info(f"レコード送信完了: {len(records)}件")
                print(f"レコード送信完了: {len(records)}件")
            
            except Exception as e:
                error_msg = f"エラーが発生しました: {str(e)}"
                logging.error(error_msg)
                print(f"エラー: {error_msg}")
                client_socket.send(error_msg.encode('utf-8'))
        
        else:
            client_socket.send("不明なリクエストです".encode('utf-8'))
    
    except Exception as e:
        logging.error(f"クライアント処理中にエラーが発生: {str(e)}")
        print(f"クライアント処理中にエラーが発生: {str(e)}")
    
    finally:
        # クライアントソケットを閉じる
        client_socket.close()


def start_server():
    """サーバーを起動する関数"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        logging.info(f"サーバーが起動しました - {HOST}:{PORT}")
        print(f"サーバーが起動しました - {HOST}:{PORT}")
        
        while True:
            client_sock, address = server.accept()
            logging.info(f"接続を受け付けました - {address[0]}:{address[1]}")
            print(f"接続を受け付けました - {address[0]}:{address[1]}")
            
            # 各クライアント接続を別スレッドで処理
            client_thread = threading.Thread(target=handle_client, args=(client_sock,))
            client_thread.daemon = True
            client_thread.start()
    
    except KeyboardInterrupt:
        logging.info("サーバーを停止します")
        print("サーバーを停止します")
    except Exception as e:
        logging.error(f"サーバーエラー: {str(e)}")
        print(f"サーバーエラー: {str(e)}")
    finally:
        server.close()

if __name__ == "__main__":
    start_server() 