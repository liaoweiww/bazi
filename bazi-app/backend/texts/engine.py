"""
易经八字APP - 文本解读引擎
根据排盘结果匹配古籍文案
"""
import json
import os
from typing import Dict, List, Optional


class TextEngine:
    """文案匹配引擎，加载JSON文案库并根据排盘结果生成解读"""

    def __init__(self, texts_dir: str = None):
        if texts_dir is None:
            texts_dir = os.path.dirname(os.path.abspath(__file__))
        self.texts_dir = texts_dir
        self._cache = {}

    def _load_json(self, filename: str) -> dict:
        """加载JSON文案文件"""
        if filename in self._cache:
            return self._cache[filename]

        filepath = os.path.join(self.texts_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._cache[filename] = data
            return data
        except FileNotFoundError:
            # 文案文件不存在时返回空结构
            return {}
        except json.JSONDecodeError:
            return {}

    def interpret(self, paipan_result: Dict) -> Dict:
        """
        根据排盘结果生成完整解读

        Args:
            paipan_result: 排盘算法返回的完整结果

        Returns:
            各维度解读字典
        """
        four_pillars = paipan_result.get('four_pillars', {})
        day_master = paipan_result.get('day_master', '')

        interpretation = {
            'four_pillars_interpret': self._interpret_four_pillars(four_pillars),
            'wuxing_interpret': self._interpret_wuxing(paipan_result),
            'shishen_interpret': self._interpret_shishen(paipan_result),
            'geju_interpret': self._interpret_geju(paipan_result),
            'yongji_interpret': self._interpret_yongji(paipan_result),
            'dayun_interpret': self._interpret_dayun(paipan_result),
            'overall': self._overall_summary(paipan_result),
        }

        return interpretation

    def _interpret_four_pillars(self, pillars: Dict) -> Dict:
        """解读四柱"""
        zhujie_data = self._load_json('zhujie.json')
        result = {}
        pillar_names = ['year', 'month', 'day', 'hour']
        pillar_labels = ['年柱', '月柱', '日柱', '时柱']

        for pname, plabel in zip(pillar_names, pillar_labels):
            pillar = pillars.get(pname, {})
            gan = pillar.get('gan', '')
            zhi = pillar.get('zhi', '')
            ganzhi = pillar.get('ganzhi', '')

            # 尝试从文案库匹配
            text = ''
            if pname in zhujie_data:
                pillar_texts = zhujie_data[pname]
                if gan in pillar_texts:
                    gan_texts = pillar_texts[gan]
                    if isinstance(gan_texts, dict) and zhi in gan_texts:
                        text = gan_texts[zhi]
                    elif isinstance(gan_texts, str):
                        text = gan_texts

            result[pname] = {
                'label': plabel,
                'ganzhi': ganzhi,
                'gan': gan,
                'zhi': zhi,
                'nayin': pillar.get('nayin', ''),
                'shishen': pillar.get('shishen', ''),
                'canggan': pillar.get('canggan', []),
                'interpretation': text or self._generate_fallback_text(gan, zhi, plabel)
            }

        return result

    def _interpret_wuxing(self, paipan_result: Dict) -> Dict:
        """解读五行旺衰"""
        wuxing_data = self._load_json('wuxing.json')
        wuxing_count = paipan_result.get('wuxing_count', {})
        strength = paipan_result.get('strength', {})

        result = {
            'counts': wuxing_count,
            'strength_level': strength.get('level', '未知'),
            'strength_score': strength.get('score', 0),
            'analysis': strength.get('details', ''),
            'overview': ''
        }

        # 匹配五行旺衰文案
        if wuxing_data.get('overview'):
            for wuxing, count_info in wuxing_count.items():
                if isinstance(count_info, dict):
                    cnt = count_info.get('count', 0)
                    score = count_info.get('score', 0)
                    if score >= 3:
                        key = f'{wuxing}旺'
                    elif score >= 2:
                        key = f'{wuxing}相'
                    elif score >= 1:
                        key = f'{wuxing}休'
                    else:
                        key = f'{wuxing}囚'
                    if key in wuxing_data['overview'] and not result['overview']:
                        result['overview'] = wuxing_data['overview'][key]

        return result

    def _interpret_shishen(self, paipan_result: Dict) -> Dict:
        """解读十神"""
        shishen_data = self._load_json('shishen.json')
        four_pillars = paipan_result.get('four_pillars', {})

        result = {}
        pillar_names = ['year', 'month', 'day', 'hour']
        pillar_labels = ['年柱', '月柱', '日柱', '时柱']

        for pname, plabel in zip(pillar_names, pillar_labels):
            pillar = four_pillars.get(pname, {})
            shishen_type = pillar.get('shishen', '')

            shishen_key_map = {
                '正印': 'zheng_yin', '偏印': 'pian_yin',
                '正官': 'zheng_guan', '七杀': 'pian_guan',
                '正财': 'zheng_cai', '偏财': 'pian_cai',
                '食神': 'shi_shen', '伤官': 'shang_guan',
                '比肩': 'bi_jian', '劫财': 'jie_cai'
            }

            key = shishen_key_map.get(shishen_type, '')
            in_key = f'in_{pname}'

            text = ''
            if key and key in shishen_data:
                ss_data = shishen_data[key]
                if isinstance(ss_data, dict):
                    text = ss_data.get(in_key, ss_data.get('general', ''))

            result[pname] = {
                'shishen': shishen_type,
                'interpretation': text or f'{shishen_type}在{plabel}'
            }

        return result

    def _interpret_geju(self, paipan_result: Dict) -> Dict:
        """解读格局"""
        geju_data = self._load_json('geju.json')
        geju = paipan_result.get('geju', {})
        geju_name = geju.get('name', '')
        geju_type = geju.get('type', '')

        text = ''
        if geju_type == '正格' and 'zheng_ge' in geju_data:
            key_map = {
                '正官格': 'zheng_guan_ge', '七杀格': 'pian_guan_ge',
                '正财格': 'zheng_cai_ge', '偏财格': 'pian_cai_ge',
                '正印格': 'zheng_yin_ge', '偏印格': 'pian_yin_ge',
                '食神格': 'shi_shen_ge', '伤官格': 'shang_guan_ge'
            }
            key = key_map.get(geju_name, '')
            if key:
                text = geju_data['zheng_ge'].get(key, '')
        elif geju_type in ['变格', '专旺格'] and 'bian_ge' in geju_data:
            text = geju_data['bian_ge'].get(geju_name, '')

        return {
            'type': geju_type,
            'name': geju_name,
            'analysis': geju.get('analysis', ''),
            'interpretation': text or geju.get('analysis', '')
        }

    def _interpret_yongji(self, paipan_result: Dict) -> Dict:
        """解读喜用神"""
        yongji = paipan_result.get('yongji', {})
        return {
            'yong_shen': yongji.get('yong_shen', []),
            'ji_shen': yongji.get('ji_shen', []),
            'xian_shen': yongji.get('xian_shen', []),
            'tiao_hou': yongji.get('tiao_hou', '')
        }

    def _interpret_dayun(self, paipan_result: Dict) -> Dict:
        """解读大运"""
        dayun_data = self._load_json('dayun.json')
        dayun = paipan_result.get('dayun', {})

        return {
            'start_age': dayun.get('start_age', 0),
            'direction': dayun.get('direction', ''),
            'dayun_list': dayun.get('dayun_list', []),
            'current_dayun': dayun.get('current_dayun', {}),
            'liunian_current': dayun.get('liunian_current', {})
        }

    def _overall_summary(self, paipan_result: Dict) -> str:
        """生成总体概述"""
        day_master = paipan_result.get('day_master', '')
        dm_wuxing = paipan_result.get('day_master_wuxing', '')
        strength = paipan_result.get('strength', {})
        strength_level = strength.get('level', '中和')
        geju = paipan_result.get('geju', {})
        yongji = paipan_result.get('yongji', {})

        yong_shen_list = yongji.get('yong_shen', [])
        yong_wuxing = [y['wuxing'] for y in yong_shen_list] if yong_shen_list else []

        summary = f'日主{dm_wuxing}({day_master})，{strength_level}。'
        if geju.get('name'):
            summary += f'格局为{geju["name"]}。'
        if yong_wuxing:
            summary += f'喜用神为{"、".join(yong_wuxing)}。'
        if yongji.get('tiao_hou'):
            summary += yongji['tiao_hou']

        return summary

    def _generate_fallback_text(self, gan: str, zhi: str, pillar_label: str) -> str:
        """生成备选解读文本（当文案库无匹配时）"""
        gan_wuxing_map = {
            '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
            '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
        }
        zhi_wuxing_map = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }

        gan_wx = gan_wuxing_map.get(gan, '')
        zhi_wx = zhi_wuxing_map.get(zhi, '')

        return f'{gan}属{gan_wx}，坐{zhi}{zhi_wx}，{pillar_label}干支组合。'


# 模块级单例
_text_engine_instance = None


def get_text_engine() -> TextEngine:
    """获取文案引擎单例"""
    global _text_engine_instance
    if _text_engine_instance is None:
        _text_engine_instance = TextEngine()
    return _text_engine_instance
