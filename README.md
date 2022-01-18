# DocumentRepeatsMarker
检测文档中前后重复的部分，并打印重复段落行号区间。最适合对大段落完全重复且段落内部不存在重复行的情况进行检查。若区域内部存在重复行，识别的重复段落将会被重复行分开。
 
# ReadlinesPostProcessing
可修改*FileLoader.line_post_process()*，在读入文件时对每行字符串修改。默认丢弃头尾空格。

# IgnoreLine
可修改*RepeatsMarker.ignore_line()*，经过该函数返回True的行会被加入忽略列表，默认若一行为空字符串或全是特殊字符，则加入该列表。仅被忽略行隔开的重复行将被归入同一重复片段。

如：
<br><br>
萧炎有了新的异火

萧炎和云韵好上了
<br><br><br><br>
萧炎有了新的异火

,,,,,,,...,.....,&^

萧炎和云韵好上了
<br><br><br><br>
将会被当作重复片段。

# Other
函数的可选参数意思基本都能从名字看出来

generate_readable_dict()的show_first_last_lines_count是指若片段较长，则截取片段的前后各x行。

index_increment是在行下标基础上增加一个增量后输出。默认为1。
 
# Sidenote
原本用于整理在贴吧连载的小说，被度娘吞吞吐吐逼得楼主可能发了多次同一章节，这样的情况。没有写自动剔除重复的东西，我太菜了没有自信不会误删。