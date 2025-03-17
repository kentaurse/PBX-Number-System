import socket
import json
import time

# サーバー設定
SERVER_HOST = '127.0.0.1'  # ローカルホストに変更
SERVER_PORT = 12345        # ポート番号
TIMEOUT = 10               # タイムアウト設定（秒）

def test_connection():
    """サーバーへの接続をテストする関数"""
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(3)
    try:
        test_socket.connect((SERVER_HOST, SERVER_PORT))
        test_socket.close()
        return True
    except Exception as e:
        print(f"接続テスト失敗: {str(e)}")
        return False

def get_voicemail_records():
    """サーバーからボイスメールレコードを取得する関数"""
    # 接続テスト
    if not test_connection():
        return "サーバーに接続できません。以下を確認してください:\n1. サーバープログラムが実行中か\n2. IPアドレスとポート番号が正しいか\n3. ファイアウォールがポートをブロックしていないか"
    
    # ソケット作成
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(TIMEOUT)  # タイムアウト設定
    
    try:
        # サーバーに接続
        print(f"サーバー {SERVER_HOST}:{SERVER_PORT} に接続しています...")
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"サーバー {SERVER_HOST}:{SERVER_PORT} に接続しました")
        
        # リクエスト送信
        client.send("get_voicemail".encode('utf-8'))
        
        # レスポンス受信
        response = b""
        while True:
            try:
                chunk = client.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                print("データ受信がタイムアウトしました。")
                break
        
        # レスポンスをデコード
        if response:
            response_str = response.decode('utf-8')
            
            # JSONとしてパース
            try:
                records = json.loads(response_str)
                return records
            except json.JSONDecodeError:
                # JSONでない場合はそのまま返す（エラーメッセージなど）
                return response_str
        else:
            return "サーバーからの応答がありませんでした。"
    
    except socket.timeout:
        return "接続がタイムアウトしました。サーバーが実行中か確認してください。"
    except ConnectionRefusedError:
        return "接続が拒否されました。サーバーが実行中か確認してください。"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"
    
    finally:
        # ソケットを閉じる
        client.close()

if __name__ == "__main__":
    print("ボイスメールレコードを取得しています...")
    records = get_voicemail_records()
    
    if isinstance(records, list):
        print(f"\n{len(records)}件のレコードを取得しました:")
        for record in records:
            print(f"インデックス: {record.get('index', 'N/A')}")
            print(f"日時: {record.get('date', 'N/A')}")
            print(f"発信者: {record.get('caller', 'N/A')}")
            print(f"通話時間: {record.get('duration', 'N/A')}")
            print(f"ステータス: {record.get('status', 'N/A')}")
            print("-" * 40)
    else:
        print(records) 