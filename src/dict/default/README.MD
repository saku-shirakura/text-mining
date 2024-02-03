# 使用方法
vibratoの辞書は、このフォルダを参照します。

まず初めに、vibrato用の辞書ファイルをこのフォルダに配置してください。

## 手順

1. 好きな辞書を[配布元](https://github.com/daac-tools/vibrato/releases/tag/v0.5.0)からダウンロードします。
    今回は、「jumandic-mecab-7_0.tar.xz」をダウンロードします。
2. jumandic-mecab-7_0.tar.xzを解凍します。
3. 解凍した結果の内容を「system.dic.zst」「NOTICE」「ライセンス表示(BSD, MITなどの名前のファイル)」をコピーし、「src/dict/default」に置きます。
4. これらの手順で、動作するはずです。

## 最終的なディレクトリの例
jumandic-mecab-7_0の場合。

jumandic-mecab-7_0という名前のファイルは、自分がインストールした辞書の名前をつけた空のファイルです。

自分で作りましょう。
````
├── BSD
├── NOTICE
├── README.MD
├── jumandic-mecab-7_0
└── system.dic.zst
````
