# DCS World EM線図測定用スクリプト


### QuickStart
### 準備
・Tacview (Advanced以上)のインストール


・DCS Worldのオプションより、SPECIAL -> Tacviewを選択

　　Real-Time Telemetry をEnabled、TCP Portを42672、Passwordなし
  
　　Remote Control をEnabled、TCP Portを42675、Passwordなし


### 測定
・EMDiaglamMeasurement.mizでFly


・同じPC上のpythonを実行できる環境で以下のコマンドを実行

　　python3 TackviewControl.py 6 1000 1 1


・1分程度で安定した状態に収束し、高度約1000 [ft]をAOA6 [deg]で飛行、旋回率11.3 [deg/s]程度になるはず

・Ctrl+Cで終了


## コマンド引数
　python3 TacviewControl.py AOACommand AltitudeCommand [PitchGain] [RollGain]
　
　AOACommand: 指定されたAOAで旋回する
 
　AltitudeCommand: 指定された高度で旋回する
 
　PitchGain: デフォルト1。高度、AOAの条件によってはAOAが振動して安定しない場合がある。その場合PitchGainを0.5～0.25程度に下げる
 
　RollGain: デフォルト1。高度、AOAの条件によってはロール角が振動して安定しない場合がある。その場合PitchGainを0.5～0.25程度に下げる


## 測定用ミッション作成
・EMDiaglamMeasurement.mizを参考にミッションを作成する

　　-マップ上に測定対象の機体1機のみ配置、パイロットはPlayer
  
　　-測定用の高度、速度にある程度合わせておく
  
　　-測定条件にあわせ機体のペイロード、燃料を設定
  
　　-ミッションのオプションからUnlimited Fuelを有効にする


