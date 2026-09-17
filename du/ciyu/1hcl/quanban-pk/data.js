const parseBank=(raw,kind)=>raw.trim().split('\n').filter(Boolean).map(line=>{const [term,zh,en,coll,context]=line.split('|');return{term,zh,en,coll,context,kind}});
const IDIOM=parseBank(`百折不挠|比喻意志坚定，无论受到多少挫折都不动摇、不退缩。|undaunted by repeated setbacks; persistent|成语用法|在公司成立初期，他遭遇许多挫折，多亏他意志坚定、_____，才有今天的成就。
班门弄斧|比喻在行家面前卖弄本领。|to show off one's skill before an expert|成语用法|谢先生是大书法家，我怎么敢在他面前_____呢？
半途而废|做事不能坚持到底，中途停止。|to give up halfway; leave something unfinished|成语用法|陈明做事总是_____，所以最终一事无成。
悲天悯人|哀叹时世艰难，怜惜人们的痛苦。|to bewail the times and pity the people|成语用法|他有_____的胸怀，每次发生天灾人祸，总会尽力帮助受灾者。
不耻下问|乐于向不如自己或地位较低的人请教，不觉得丢脸。|not feel ashamed to ask and learn from others|成语用法|学习要_____，遇到不懂的问题就主动请教。
不亢不卑|既不高傲，也不自卑，态度恰当有分寸。|neither haughty nor humble|成语用法|面对外国来宾，他态度_____，给人留下很好的印象。
不苟言笑|不随便说笑，形容态度庄重严肃。|serious in speech and manner|成语用法|工作时_____的他，一到休息时间却十分健谈。
不可救药|比喻已经到了无法挽救的地步。|incurable; hopeless|成语用法|他终日沉迷于赌博，若再不改变，恐怕真的到了_____的地步。
不劳而获|不付出劳动，却想得到成果或利益。|to gain without working for it|成语用法|他沉迷赌博，希望能够_____，一夜成为富翁。
不务正业|不做本职工作，却去做其他不正当或无关的事。|not attend to one's proper duties|成语用法|他整天游手好闲、_____，家人都为他担心。
不翼而飞|比喻物品突然丢失或消失。|to disappear without a trace|成语用法|我明明把钱包放在桌上，转眼间却_____了。
不知所措|不知道怎么办才好，形容慌乱或为难。|to be at a loss; not know what to do|成语用法|得知工厂下星期停工，许多员工一时_____。
不自量力|过高估计自己的能力或实力。|to overestimate one's own abilities|成语用法|那支球队球技还不成熟，却主动挑战冠军队，真是_____。
差强人意|大体上还能使人满意。|barely satisfactory; just passable|成语用法|那几首诗写得不怎么样，只有这一首还算_____。
长年累月|形容经过很长的时间。|for months and years; over a long period|成语用法|他_____地超负荷工作，又不注意休息，终于病倒了。
长袖善舞|比喻善于凭借条件钻营取巧、拉拢关系，常含贬义。|to be skilful at social manoeuvring|成语用法|他在商场上_____，很会拉拢关系，因此生意越做越大。
嗤之以鼻|表示轻视、看不起。|to snort in contempt; to scorn|成语用法|对于他为了讨好领导而低声下气的做法，我十分反感，甚至_____。
持之以恒|长久坚持下去。|to persevere; to persist|成语用法|学习需要_____，每天坚持一点，才能慢慢进步。
重蹈覆辙|比喻不吸取教训，再犯过去的错误。|to repeat the same mistake|成语用法|上次失败后，我们一定要认真总结原因，避免_____。
出尔反尔|言行反复无常，前后不一致。|to go back on one's word|成语用法|小明说话总是_____，答应过的事常常又反悔，所以大家不太相信他。
出类拔萃|品行或才干高出同辈，十分优秀。|to stand out from the crowd; outstanding|成语用法|他在众多年轻设计师中表现_____，很快受到公司的重用。
出人头地|指成就突出，超过一般人。|to distinguish oneself; to succeed|成语用法|克明每天努力读书充实自己，希望将来能够_____。
处之泰然|面对困难或意外时沉着镇定，态度从容。|to handle a situation calmly|成语用法|他经验丰富，面对突如其来的状况总能_____，迅速处理问题。
吹毛求疵|故意挑剔细小的毛病。|to nitpick; to find fault|成语用法|他总爱对别人的小错误_____，让同事压力很大。
垂涎三尺|形容非常羡慕或很想得到，多指对食物或物品十分向往。|to drool with envy; to crave|成语用法|看到桌上刚出炉的烤鸭，弟弟馋得_____。
从善如流|能很快接受别人正确的意见或善意的劝告。|to readily accept good advice|成语用法|校长_____，听取师生建议后马上调整安排。
粗制滥造|制作粗劣，不讲质量。|to produce shoddy work|成语用法|这批玩具因为厂家_____，没用多久就损坏了。
大公无私|办事公正，没有私心。|selfless and impartial|成语用法|他处理班级事务一向_____，从不会偏袒自己的好友。
大言不惭|说大话却不觉得惭愧。|to boast without shame|成语用法|他从未参加过比赛，却_____地说自己一定能夺冠。
当机立断|在关键时刻立即作出决定。|to make a prompt decision|成语用法|火警响起时，老师_____，马上带学生撤离。
当仁不让|遇到应该做的事，主动承担，不推让。|to take on a responsibility without hesitation|成语用法|班级需要代表参加义工活动时，他_____，主动报名。
道貌岸然|外表严肃正经，实际上品德不好，含讽刺意味。|sanctimonious; feigning righteousness|成语用法|他表面上_____，私下却经常欺骗别人。
德高望重|品德高尚，声望很高，受到大家尊敬。|highly respected|成语用法|这位_____的老校长退休后，师生仍常去探望他。
得过且过|只求眼前过得去，不作长远打算。|to muddle along; drift along|成语用法|如果学习总是_____，不愿改进弱点，成绩很难提高。
得意忘形|因得意而失去常态，表现得过分骄傲。|to get carried away by success|成语用法|他刚赢了一场比赛就_____，竟开始嘲笑对手。
掉以轻心|对事情采取轻率态度，不认真重视。|to let one's guard down; take lightly|成语用法|虽然这次测验不难，我们也不能_____，还是要认真检查。
独善其身|只顾自己做好，不关心别人或社会。|to look after only one's own interests|成语用法|面对公共问题，我们不能只求_____，也应该关心别人。
对牛弹琴|比喻对不懂道理的人讲深奥的道理，或对不合适的对象说话。|to address the wrong audience|成语用法|对完全不懂音乐的人讲复杂乐理，简直是_____。
对症下药|比喻针对问题的原因采取有效办法。|to suit the remedy to the problem|成语用法|找出学习退步的真正原因后，老师才能_____，帮助他改进。
多多益善|越多越好。|the more, the better|成语用法|社区活动需要志愿者，人手当然_____。
耳濡目染|经常听到、看到，不知不觉受到影响。|to be influenced by what one often sees and hears|成语用法|他从小跟着父亲学书法，_____之下，也渐渐喜欢上书法。
发人深省|启发人深入思考。|thought-provoking; to set people thinking|成语用法|这部短片揭示网络欺凌的后果，内容十分_____。
发扬光大|使好的传统、作风等进一步发展和扩大。|to carry forward and develop|成语用法|我们应该把优秀的传统文化继续_____，让更多年轻人了解。
反唇相讥|受到责难时反过来讥讽对方。|to answer back sarcastically|成语用法|面对同学的批评，他没有虚心听取，反而_____，结果争执升级。
防患未然|在祸患发生前先采取措施预防。|to prevent trouble before it happens|成语用法|学校定期举行消防演习，就是为了_____。
匪夷所思|事情奇怪得令人难以想象。|unimaginable; unbelievable|成语用法|他明知作弊会受处罚，竟还公开作弊，实在_____。
废寝忘食|顾不得睡觉，忘记吃饭，形容非常专心努力。|to forget sleep and food; work very hard|成语用法|为了尽快找出治疗癌症的方法，研究人员_____地进行研究。
纷至沓来|形容接连不断地到来。|to come in a continuous stream|成语用法|公司张贴招收新员工的告示后，求职者_____。
奉公守法|按公事办事，遵守法律和规定。|law-abiding; to observe the law|成语用法|如果每个人都能_____，社会秩序自然会更安定。
敷衍塞责|工作不认真负责，只表面应付了事。|to perform one's duty carelessly|成语用法|他这种_____的工作态度，很难得到老板的信任。
赴汤蹈火|比喻不避艰险，勇往直前。|to go through fire and water; defy danger|成语用法|只要国家有需要，即使_____，我们也在所不辞。
改过自新|改正错误，重新做人。|to mend one's ways and make a fresh start|成语用法|从监狱释放出来后，俊明决定_____，重新开始生活。
改邪归正|停止做坏事，回到正道。|to abandon evil and return to the right path|成语用法|只要你愿意_____，大家都会给你重新开始的机会。
高瞻远瞩|比喻眼光远大，看得长远。|far-sighted; to look far ahead|成语用法|董事长_____，几年前就开始布局新市场，公司因此取得今天的成就。
高枕无忧|比喻没有忧虑，也可形容放松警惕。|to rest easy; to be free from worry|成语用法|即使事情暂时顺利，我们也不能以为从此可以_____。
各有千秋|各有各的优点和特色。|each has its own merits|成语用法|这次参赛作品_____，评审一时难以取舍。
根深蒂固|比喻基础很深，不容易动摇或改变。|deep-rooted; ingrained|成语用法|这种错误观念在人们心中已经_____，很难在短期内改变。
功亏一篑|比喻事情只差最后一点却没有完成。|to fail for lack of a final effort|成语用法|试验马上就要成功了，大家千万不能松懈，否则可能_____。
勾心斗角|比喻彼此用尽心机，明争暗斗。|to scheme against each other|成语用法|几位经理为了升职彼此_____，办公室气氛越来越差。
苟且偷安|只顾眼前安逸，不顾将来。|to seek temporary ease and comfort|成语用法|国难当前，他却只顾眼前安稳，选择_____，令人失望。
孤陋寡闻|学识浅、见闻少。|ignorant and ill-informed|成语用法|你连我国总理是谁都不知道，未免太_____了吧！
沽名钓誉|用不正当手段谋取名声和荣誉。|to fish for fame; seek undeserved reputation|成语用法|他并非真心做慈善，只是想借活动_____。
孤掌难鸣|比喻一个人的力量有限，难以成事。|one person alone cannot achieve much|成语用法|班长一个人想改变全班学习风气，却发现_____，于是主动邀请同学一起参与。
孤注一掷|把所有力量或本钱押在一次行动上，冒险求成功。|to risk everything on one venture|成语用法|他屡赌屡输，最后竟决定_____，把剩下的钱全押上。
寡不敌众|人少的一方抵挡不住人多的一方。|to be outnumbered|成语用法|他被多人围攻，最后因_____而败下阵来。
光明正大|襟怀坦白，言行正派。|open and aboveboard; upright|成语用法|志强做事一向_____，从不暗中陷害别人。
裹足不前|因为顾虑或害怕而停步不前。|to hesitate and refuse to move forward|成语用法|面对困难，我们应该想办法突破，不能_____。
海底捞针|比喻极难找到。|like looking for a needle in the sea|成语用法|在人山人海中寻找一枚小戒指，简直像_____。
骇人听闻|使人听了非常震惊。|shocking; appalling|成语用法|警方侦破了一起_____的虐待案件，社会各界十分震惊。
害群之马|比喻危害集体的人。|a harmful member of a group|成语用法|这名警员贪污受贿，损害警队声誉，成了警界的_____。
饱经风霜|经历过很多艰难困苦。|to have experienced many hardships|成语用法|这位老人一生漂泊，脸上刻满岁月痕迹，一看就是_____。
里程碑|比喻发展过程中具有重大意义的事件。|milestone|成语用法|第一条地铁线开通，是我国交通发展史上的重要_____。
赞不绝口|不停地称赞。|to be full of praise|成语用法|游客品尝这道本地美食后，都_____。
不偏不倚|不偏向任何一方，形容公正。|impartial; fair|成语用法|裁判的判决_____，双方都接受结果。
一帆风顺|比喻事情进行顺利，没有阻碍。|smooth sailing|成语用法|创业不可能总是_____，遇到挫折时要想办法解决。
开卷有益|打开书本阅读就会有收获，指读书有好处。|reading is beneficial|成语用法|常言道“_____”，多阅读能增长知识。
人人皆晓|每个人都知道。|known to everyone|成语用法|鱼尾狮是新加坡_____的旅游标志。
慢条斯理|形容说话做事慢而有条理，不慌不忙。|unhurried and methodical|成语用法|大家急得团团转，他却仍_____地收拾文件。
安然无恙|平安，没有受到损害。|safe and sound|成语用法|地震后，大家得知失联的队员_____，终于松了一口气。
一马平川|形容广阔平坦的地势。|a vast stretch of flat land|成语用法|站在高处望去，前方_____，几乎看不到起伏的山地。
全力以赴|把全部力量投入进去。|to give one's all; go all out|成语用法|为了即将到来的决赛，队员们决定_____，争取最好成绩。`,'idiom');
const DATA={idiom:IDIOM};