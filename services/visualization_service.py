import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import io

class VisualizationService:
    def generate_skill_cloud(self, skills: list) -> bytes:
        if not skills:
            return None
        
        skill_dict = {s["skill_name"]: s["count"] * 10 for s in skills}
        
        wordcloud = WordCloud(
            width=800,
            height=600,
            background_color='white',
            colormap='viridis',
            max_words=50,
            font_path='simhei.ttf' if self._font_exists('simhei.ttf') else None,
            prefer_horizontal=0.8
        )
        
        wordcloud.generate_from_frequencies(skill_dict)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf.getvalue()
    
    def _font_exists(self, font_name: str) -> bool:
        import matplotlib.font_manager as fm
        fonts = [f.name for f in fm.fontManager.ttflist]
        return font_name.split('.')[0] in fonts
    
    def generate_skill_bar_chart(self, skills: list) -> bytes:
        if not skills:
            return None
        
        sorted_skills = sorted(skills, key=lambda x: x["count"], reverse=True)[:10]
        skill_names = [s["skill_name"] for s in sorted_skills]
        skill_counts = [s["count"] for s in sorted_skills]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(skill_names, skill_counts, color='#4CAF50')
        
        plt.title('技能分布')
        plt.xlabel('技能')
        plt.ylabel('出现次数')
        plt.xticks(rotation=45, ha='right')
        
        for bar, count in zip(bars, skill_counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                     str(count), ha='center', va='bottom')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf.getvalue()