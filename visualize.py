from wordcloud import WordCloud
import matplotlib.pyplot as plt

def visualize(word_list_counted, output_path="wordcloud.png"):
    wordcloud = WordCloud(width=1920, height=1080, background_color="#0f172a", colormap="cool")
    wordcloud.generate_from_frequencies(word_list_counted)
    wordcloud.to_file("wordcloud.png")
    
    return output_path