import itertools
import os
from pathlib import Path

import vibrato
import zstandard

# 以下のストップワードリストは、Slothlibを利用して、作成されています。
#
# コピーライト:
# Copyright (c) 2007, 京都大学情報学研究科社会情報学専攻 田中克己研究室 All rights reserved.
#
# ライセンス:
# SlothLib
#
# Copyright (c) 2007, 京都大学情報学研究科社会情報学専攻 田中克己研究室
# All rights reserved.
#
# ソースコード形式かバイナリ形式か、変更するかしないかを問わず、以下の条件を満たす場合に限り、再頒布および使用が許可されます。
#
# ソースコードを再頒布する場合、上記の著作権表示、本条件一覧、および下記免責条項を含めること。
#
# バイナリ形式で再頒布する場合、頒布物に付属のドキュメント等の資料に、上記の著作権表示、本条件一覧、および下記免責条項を含めること。
#
# 書面による特別の許可なしに、本ソフトウェアから派生した製品の宣伝または販売促進に、
# 京都大学情報学研究科社会情報学専攻田中克己研究室の名前またはコントリビューターの名前を使用してはならない。
#
# 本ソフトウェアは、著作権者およびコントリビューターによって「現状のまま」提供されており、
# 明示黙示を問わず、商業的な使用可能性、および特定の目的に対する適合性に関する暗黙の保証も含め、またそれに限定されない、
# いかなる保証もありません。著作権者もコントリビューターも、事由のいかんを問わず、 損害発生の原因いかんを問わず、
# かつ責任の根拠が契約であるか厳格責任であるか（過失その他の）不法行為であるかを問わず、仮にそのような損害が発生する可能性を知らされていたとしても、
# 本ソフトウェアの使用によって発生した （代替品または代用サービスの調達、使用の喪失、データの喪失、利益の喪失、業務の中断も含め、またそれに限定されない）
# 直接損害、間接損害、偶発的な損害、特別損害、懲罰的損害、または結果損害について、一切責任を負わないものとします。
# プロジェクトページ: https://ja.osdn.net/projects/slothlib/
stop_word = [
    # "あそこ", "あたり", "あちら", "あっち", "あと", "あな", "あなた", "あれ", "いくつ", "いつ", "いま", "いや",
    # "いろいろ", "うち", "おおまか", "おまえ", "おれ", "がい", "かく", "かたち", "かやの", "から", "がら", "きた",
    # "くせ", "ここ", "こっち", "こと", "ごと", "こちら", "ごっちゃ", "これ", "これら", "ごろ", "さまざま", "さらい",
    # "さん", "しかた", "しよう", "すか", "ずつ", "すね", "すべて", "ぜんぶ", "そう", "そこ", "そちら", "そっち", "そで",
    # "それ", "それぞれ", "それなり", "たくさん", "たち", "たび", "ため", "だめ", "ちゃ", "ちゃん", "てん", "とおり",
    # "とき", "どこ", "どこか", "ところ", "どちら", "どっか", "どっち", "どれ", "なか", "なかば", "なに", "など", "なん",
    # "はじめ", "はず", "はるか", "ひと", "ひとつ", "ふく", "ぶり", "べつ", "へん", "ぺん", "ほう", "ほか", "まさ",
    # "まし", "まとも", "まま", "みたい", "みつ", "みなさん", "みんな", "もと", "もの", "もん", "やつ", "よう", "よそ",
    # "わけ", "わたし", "ハイ", "上", "中", "下", "字", "年", "月", "日", "時", "分", "秒", "週", "火", "水", "木", "金",
    # "土", "国", "都", "道", "府", "県", "市", "区", "町", "村", "各", "第", "方", "何", "的", "度", "文", "者", "性",
    # "体", "人", "他", "今", "部", "課", "係", "外", "類", "達", "気", "室", "口", "誰", "用", "界", "会", "首", "男",
    # "女", "別", "話", "私", "屋", "店", "家", "場", "等", "見", "際", "観", "段", "略", "例", "系", "論", "形", "間",
    # "地", "員", "線", "点", "書", "品", "力", "法", "感", "作", "元", "手", "数", "彼", "彼女", "子", "内", "楽", "喜",
    # "怒", "哀", "輪", "頃", "化", "境", "俺", "奴", "高", "校", "婦", "伸", "紀", "誌", "レ", "行", "列", "事", "士",
    # "台", "集", "様", "所", "歴", "器", "名", "情", "連", "毎", "式", "簿", "回", "匹", "個", "席", "束", "歳", "目",
    # "通", "面", "円", "玉", "枚", "前", "後", "左", "右", "次", "先", "春", "夏", "秋", "冬", "一", "二", "三", "四",
    # "五", "六", "七", "八", "九", "十", "百", "千", "万", "億", "兆", "下記", "上記", "時間", "今回", "前回", "場合",
    # "一つ", "年生", "自分", "ヶ所", "ヵ所", "カ所", "箇所", "ヶ月", "ヵ月", "カ月", "箇月", "名前", "本当", "確か",
    # "時点", "全部", "関係", "近く", "方法", "我々", "違い", "多く", "扱い", "新た", "その後", "半ば", "結局", "様々",
    # "以前", "以後", "以降", "未満", "以上", "以下", "幾つ", "毎日", "自体", "向こう", "何人", "手段", "同じ", "感じ",
]

delimiter = [
    '.', '。', '!', '?', '！', '？'
]

target_part_of_speech = [
    '名詞', '動詞', '形容詞', '形容動詞', '感動詞', '副詞'
]


class Sequences:
    # 文章ごとの単語の集合
    sequence_set: list[set] = []
    # 文章全体のトークンの集合
    all_token_set: set = set()
    # 全体の使われているトークンの出現回数
    count_and_tokens: dict = {}
    # 全体の使われているトークンの数
    token_count: int = 0

    # 文章の登録
    def add_sequence(self, token_list: list[str]):
        self.sequence_set.append(set(token_list))
        for token in token_list:
            self.__add_token(token)

    # トークンの登録
    def __add_token(self, token: str):
        # トークンのバリデーション
        if token == "" or token is None:
            return
        if self.count_and_tokens.get(token) is None:
            # トークンがまだない
            # 1に設定
            self.count_and_tokens[token] = 1
        else:
            # トークンがある
            # 1を追加
            self.count_and_tokens[token] += 1
        # トークン数をインクリメント
        self.token_count += 1
        self.all_token_set.add(token)

    # ある２つのトークンについての、文章中の出現頻度を求める
    def __count_tokens_freq(self, token_set: set):
        if len(token_set) > 2:
            raise RuntimeError("Invalid token_set length")
        count_tokens_freq: dict[str, int] = {}
        count_a_and_b_freq = 0
        list_token_set = list(token_set)
        # すべての文章をイテレートする。
        for sequence in self.sequence_set:
            if len(sequence) <= 1:
                continue
            # aがすでに含まれているかどうかのフラグ
            tmp_is_in_a = False
            # aが含まれているかどうかの確認
            # 含まれているならば + 1
            if list_token_set[0] in sequence:
                if count_tokens_freq.get(list_token_set[0]) is None:
                    count_tokens_freq[list_token_set[0]] = 0
                count_tokens_freq[list_token_set[0]] += 1
                tmp_is_in_a = True
            # bが含まれているかどうかの確認
            # 含まれているならば + 1
            if list_token_set[1] in sequence:
                if count_tokens_freq.get(list_token_set[1]) is None:
                    count_tokens_freq[list_token_set[1]] = 0
                count_tokens_freq[list_token_set[1]] += 1
                # aが含まれていれば、追加で[a and b]も + 1
                if tmp_is_in_a:
                    count_a_and_b_freq += 1
        # count_tokens_freq: [aが単体で文章中に出現する回数, bが単体で文章中に出現する回数]
        # count_a_and_b_freq: n(aとbが同時に文章中に出現する回数)
        return count_tokens_freq, count_a_and_b_freq

    # ある2つのトークンについてのジャッカード係数を算出
    def calc_jaccard(self, token_set: set) -> tuple[float, int]:
        count_tokens_freq, count_a_and_b_freq = self.__count_tokens_freq(token_set)
        try:
            # n(a & b) / n(a | b) = n(a & b) / (n(a) + n(b) - n(a & b))
            return count_a_and_b_freq / (sum(count_tokens_freq.values()) - count_a_and_b_freq), count_a_and_b_freq
        except ZeroDivisionError:
            return 1.0, 0

    # ある2つのトークンについてのダイス係数を算出
    def calc_dice(self, token_set: set) -> tuple[float, int]:
        count_tokens_freq, count_a_and_b_freq = self.__count_tokens_freq(token_set)
        try:
            # (2 * n(a & b)) / (n(a) + n(b)) = n(a & b) / (n(a) + n(b))
            return (2 * count_a_and_b_freq) / sum(count_tokens_freq.values()), count_a_and_b_freq
        except ZeroDivisionError:
            return 1.0, 0

    # ある2つのトークンについてのシンプソン係数を算出
    def calc_simpson(self, token_set: set) -> tuple[float, int]:
        count_tokens_freq, count_a_and_b_freq = self.__count_tokens_freq(token_set)
        try:
            # n(a & b) / min(n(a), n(b))
            return count_a_and_b_freq / min(count_tokens_freq.values()), count_a_and_b_freq
        except ZeroDivisionError:
            if sum(count_tokens_freq.values()) == 0:
                return 1.0, 0
            return 0.0, 0


class VibratoHelper:
    v_instance: vibrato.Vibrato

    def __init__(self):
        self.change_dict(
            str(os.path.join(str(Path(os.path.dirname(__file__)).resolve()), 'dict/default/system.dic.zst')))

    # 辞書を変更する。
    def change_dict(self, dict_path: str):
        # 以下は、python-vibratoのexamplesからの抜粋です。
        # 元々のソースコードの著作権は、python-vibratoの著作権者にあります。
        # python-vibratoは、デュアルライセンスであり、MITライセンスとApacheライセンスのいずれかの条件で利用できます。(2024-02-03時点)
        # 注意: ここでは、MIT-Licenseの条件のもと抜粋しています。
        # ライセンスの変更などで、利用条件が変わった場合などに気づかず、
        # 対応がなされていなかった場合は、github issuesに投稿してください。
        # 確認後、対応いたします。
        # 利用条件および、抜粋元は以下の通りです。
        # 抜粋元: https://github.com/daac-tools/python-vibrato/blob/v0.2.0/docs/source/examples.rst
        # ライセンスの詳細: https://opensource.org/license/mit/
        # リポジトリ: https://github.com/daac-tools/python-vibrato
        dctx = zstandard.ZstdDecompressor()
        with open(dict_path, 'rb') as fp:
            with dctx.stream_reader(fp) as dict_reader:
                self.v_instance = vibrato.Vibrato(dict_reader.read())

    # テキストを分かち書きする。
    def tokenize_text(self, text: str):
        return self.v_instance.tokenize(text)

    # トークンを正規化
    def tokenize_normalized(self, text: str):
        token_list = [[], ]
        tokenized_data = self.tokenize_text(text)
        for token in tokenized_data:
            # 文ごとに区切る
            if token.surface() in delimiter:
                token_list.append([])
                continue
            # 対象とする品詞があれば、それに制限する。(ホワイトリストモード)
            # なければ、すべてについて表示。
            if len(target_part_of_speech) != 0:
                if token.feature().split(",")[0] not in target_part_of_speech:
                    continue
            #
            normalized_token = token.feature().split(',')[4]
            if normalized_token == '*':
                normalized_token = token.surface()
            # STOP WORD
            if normalized_token in stop_word:
                continue
            token_list[-1].append(normalized_token)
        # 末尾にある空のリストを削除する。
        if len(token_list[-1]) == 0:
            token_list.pop()
        return token_list


class TextMiner:
    sequence: Sequences
    tokenizer: VibratoHelper

    def __init__(self):
        self.tokenizer = VibratoHelper()
        self.sequence = Sequences()

    def add_from_file(self, text_path: str):
        with open(text_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for text in lines:
                new_line = text.replace('\n', '')
                r_newline = new_line.replace('\r', '')
                self.add_text(r_newline)

    def add_text(self, text: str):
        sequences = self.tokenizer.tokenize_normalized(text)
        for i_seq in sequences:
            self.sequence.add_sequence(i_seq)

    # thresholdを超えるのすべての組み合わせについてのジャッカード係数を列挙する。
    def calculate_all_jaccard_score(self, threshold=0.0, max_elements=20):
        weighted_all_jaccard_scores = dict()
        blacklist = dict()
        # 文章をイテレート
        for sequence in self.sequence.sequence_set:
            # 現在の文章から2つ選択したすべての組み合わせをイテレート。
            for token_set in itertools.combinations(sequence, 2):
                # すでに計算済みであれば、計算しない。
                if weighted_all_jaccard_scores.get(token_set) is not None:
                    continue
                if blacklist.get(token_set) is not None:
                    continue
                # ジャッカード係数を計算し、それを登録する。
                jaccard_score, count_a_and_b_freq = self.sequence.calc_jaccard(token_set)
                if jaccard_score > threshold:
                    weighted_all_jaccard_scores[token_set] = jaccard_score * count_a_and_b_freq
                else:
                    blacklist[token_set] = True
        sorted_jaccard_scores = sorted(weighted_all_jaccard_scores.items(), reverse=True, key=lambda x: x[1])
        print(sorted_jaccard_scores)
        result = []
        for i in range(0, max_elements if len(sorted_jaccard_scores) >= max_elements else len(sorted_jaccard_scores)):
            result.append(sorted_jaccard_scores[i][0])
        return result
