const parseBank=(raw,kind)=>raw.trim().split('\n').filter(Boolean).map(line=>{const [term,zh,en,coll,context,group]=line.split('|');return{term,zh,en,coll,context,group,kind}});
const IDIOM=parseBank(`百折不挠|比喻意志坚定，受到多次挫折也不退缩。|undaunted by repeated setbacks; persistent|坚持|创业初期，他接连失败，但仍然_____，最终把公司经营起来。|A
班门弄斧|比喻在行家面前卖弄本领。|to show off one's skill before an expert|成语用法|谢先生是大书法家，我怎么敢在他面前_____呢？|C
半途而废|做事不能坚持到底，中途停止。|to give up halfway; leave something unfinished|成语用法|陈明做事总是_____，所以很多计划都没有完成。|A
悲天悯人|哀叹世事艰难，同情人们的痛苦。|to feel compassion for people's suffering|成语用法|每逢天灾，他总会主动捐款帮助灾民，可见他有_____的情怀。|B
不耻下问|乐于向不如自己的人请教，不觉得难为情。|not be ashamed to ask and learn from others|成语用法|学习新知识时，即使对方年纪比自己小，我们也应_____。|C
不亢不卑|既不高傲，也不自卑，态度得体有分寸。|neither arrogant nor humble|成语用法|面对外国来宾，他态度得体，表现得_____。|B
不苟言笑|不随便说笑，形容态度庄重严肃。|serious in speech and manner|成语用法|工作时_____的他，休息时却很喜欢和同事开玩笑。|B
不可救药|比喻情况严重到无法挽救。|incurable; hopeless|成语用法|他沉迷赌博，多次劝告仍不肯改变，大家都觉得他已经_____。|A
不劳而获|自己不劳动，却想得到成果或利益。|to gain without working for it|成语用法|他只想靠别人赚钱，自己却不肯付出，总想着_____。|B
不务正业|不做本职或正当的事，却去做别的事情。|to neglect one's proper duties|成语用法|他长期_____，把工作丢在一旁，整天只顾玩乐。|B
不翼而飞|比喻物品忽然丢失或消失。|to disappear without a trace|成语用法|我刚放在桌上的钱包，转眼就_____了。|A
不知所措|不知道怎么办才好，形容慌乱或为难。|to be at a loss; not know what to do|成语用法|听到突如其来的坏消息，他一时_____。|B
不自量力|过高估计自己的能力。|to overestimate one's abilities|成语用法|那支新球队竟主动挑战卫冕冠军，大家都说他们有点_____。|C
差强人意|大体上还算让人满意。|barely satisfactory; acceptable|成语用法|几份设计方案都不理想，只有最后一份还算_____。|A
长年累月|形容经过很长时间。|for many months and years; over a long time|成语用法|他_____在烈日下工作，终于积劳成疾。|D
长袖善舞|比喻善于交际应酬、钻营取巧，多含贬义。|to be skilful at social manoeuvring|成语用法|他很会经营人际关系，在商场上_____，为自己争取到不少机会。|B
嗤之以鼻|用冷笑表示轻视、看不起。|to snort in contempt; to disdain|成语用法|对于这种投机取巧的做法，他一向_____。|B
持之以恒|长久坚持下去。|to persevere; to persist|成语用法|学语言不能三天打鱼两天晒网，必须_____。|A
重蹈覆辙|不吸取教训，再犯过去的错误。|to repeat the same mistakes|成语用法|这次我们必须吸取教训，避免_____。|A
出尔反尔|言行反复，前后不一致。|to go back on one's word|成语用法|他常常_____，所以大家都不敢再相信他的承诺。|B
出类拔萃|品行或才能高出同辈，非常突出。|to stand out from the crowd; outstanding|成语用法|她在众多参赛者中表现_____，最终获选代表学校。|A
出人头地|指成就突出，超过一般人。|to distinguish oneself; to achieve success|成语用法|他努力进修，希望将来能_____，让家人过上更好的生活。|A
处之泰然|面对困难或突发情况时沉着镇定，不慌张。|to handle a situation calmly|成语用法|面对突发状况，他仍能_____，有条不紊地处理问题。|B
吹毛求疵|故意挑剔细小的毛病。|to find fault with trivial things; to nitpick|成语用法|这份报告已经很完整了，他却还是_____，不停挑小毛病。|B
垂涎三尺|形容非常贪馋或十分羡慕、想得到。|to drool with envy; to crave|成语用法|看到刚出炉的烤鸭，弟弟馋得_____。|B
从善如流|很乐意听取正确的意见或善意的劝告。|to readily accept good advice|成语用法|王经理愿意听取员工的合理建议，总能_____。|B
粗制滥造|制作粗劣，不讲求质量。|to produce shoddy work; rough and careless workmanship|成语用法|这家工厂为了赶工而_____，产品很快出现问题。|B
大公无私|办事公正，没有私心。|selfless and impartial|成语用法|校长处理奖学金申请时一视同仁，表现得_____。|B
大言不惭|说大话却不觉得羞愧。|to boast shamelessly|成语用法|他从没受过训练，却_____地说自己一定能拿冠军。|B
当机立断|在关键时刻马上作出决定。|to make a prompt decision|成语用法|火警响起后，老师_____，马上带学生撤离。|D
当仁不让|遇到应该做的事，主动承担，不推辞。|to not decline a rightful responsibility|成语用法|学校需要有人负责义卖活动，他_____地接下任务。|D
道貌岸然|外表严肃正派，实际常含虚伪、装腔作势的意思。|sanctimonious; pretending to be righteous|成语用法|他表面上_____，私下却常占别人便宜。|B
德高望重|品德高尚，声望很高，受人尊敬。|highly respected for virtue and reputation|成语用法|这位_____的老校长深受师生敬爱。|B
得过且过|只求眼前过得去，不作长远打算。|to muddle along; drift through life|成语用法|如果每天都抱着_____的态度，不认真学习，很难进步。|B
得意忘形|因太得意而失去常态。|to get carried away by success|成语用法|他刚赢一场比赛就_____，到处炫耀。|B
掉以轻心|对事情采取轻率态度，不认真重视。|to let one's guard down; take lightly|成语用法|虽然对手实力不强，我们也不能_____。|B
独善其身|只顾自己，不关心他人或集体。|to look after oneself alone and ignore others|成语用法|公共问题需要大家参与，不能只想_____，对别人的困难不闻不问。|B
对牛弹琴|比喻对不懂道理的人讲深奥的道理，白费口舌。|to address the wrong audience; to play the lute to a cow|成语用法|跟完全不懂音乐的人讲复杂乐理，简直是_____。|C
对症下药|针对具体问题采取有效办法。|to suit the remedy to the problem|成语用法|找出学习退步的真正原因后，老师才能_____。|C
多多益善|越多越好。|the more, the better|成语用法|阅读好书当然是_____，只要懂得选择适合自己的内容。|D
耳濡目染|经常听到看到，不知不觉受到影响。|to be influenced by what one constantly sees and hears|成语用法|从小跟着父亲做木工，他_____，也学会不少技巧。|C
发人深省|能启发人深入思考。|thought-provoking; to set people thinking|成语用法|这部纪录片揭示浪费食物的问题，内容十分_____。|C
发扬光大|把好的传统、作风等进一步发展和扩大。|to carry forward and develop|成语用法|我们有责任把优秀传统文化继续_____。|A
反唇相讥|受到指责时反过来讥讽对方。|to retort sarcastically|成语用法|被同学讽刺后，他没有解释，反而马上_____。|B
防患未然|在祸患发生前先采取措施预防。|to prevent trouble before it happens|成语用法|学校定期进行消防演习，就是为了_____。|D
匪夷所思|形容事情奇怪到让人难以想象。|unbelievable; beyond imagination|成语用法|他的做法实在_____，大家都想不通。|C
废寝忘食|顾不得睡觉，忘记吃饭，形容非常专心努力。|to forget sleep and meals; work extremely hard|成语用法|为了尽早找出治疗方法，研究人员_____地进行研究。|A
纷至沓来|形容接连不断地到来。|to arrive in a continuous stream|成语用法|招聘启事一刊出，求职者便_____。|D
奉公守法|奉公行事，遵守法令，形容办事守规矩。|to be law-abiding|成语用法|如果每个人都能_____，社会秩序就会更加稳定。|B
敷衍塞责|工作不认真，只是表面应付责任。|to do one's duty carelessly; be perfunctory|成语用法|他这种_____的工作态度，很难得到老板的信任。|B
赴汤蹈火|比喻不避艰险，勇往直前。|to go through fire and water; brave all dangers|成语用法|为了救出受困者，消防员即使_____也在所不辞。|D
改过自新|改正错误，重新做人。|to mend one's ways and make a fresh start|成语用法|从监狱释放后，俊明决定_____，重新生活。|A
改邪归正|离开邪路，回到正道，不再做坏事。|to abandon wrongdoing and return to the right path|成语用法|只要你愿意_____，大家都会给你重新开始的机会。|A
高瞻远瞩|比喻眼光远大，看得长远。|far-sighted; visionary|成语用法|董事长能够提早布局新市场，可见他十分_____。|C
高枕无忧|比喻以为平安无事而完全放心；有时含缺乏警觉的意思。|to rest easy without worries; become complacent|成语用法|问题虽然暂时解决了，我们也不能就此_____。|B
各有千秋|各有各的优点或特色。|each has its own merits|成语用法|两份设计风格不同，却_____，评审难以取舍。|D
根深蒂固|比喻基础深厚，难以动摇或改变。|deep-rooted; ingrained|成语用法|这种偏见在社会上已经_____，短时间内很难改变。|B
功亏一篑|比喻事情只差最后一点却没有完成。|to fail at the last step; fall short of success|成语用法|项目只差最后一步，大家千万不能松懈，以免_____。|A
勾心斗角|比喻互相明争暗斗、彼此算计。|to scheme and fight against one another|成语用法|几位经理为了升职彼此_____，严重影响团队合作。|B
苟且偷安|只顾眼前安逸，不考虑长远。|to seek temporary ease; live for the moment|成语用法|国难当前，我们不能_____，而应主动承担责任。|B
孤陋寡闻|学识浅薄，见闻不广。|ignorant and ill-informed|成语用法|他从不读书看报，对外界变化一无所知，显得有些_____。|C
沽名钓誉|用不正当手段骗取名声。|to fish for fame; seek undeserved reputation|成语用法|他参加慈善活动只是为了上新闻，借机_____。|B
孤掌难鸣|比喻一个人力量有限，难以成事。|one person alone cannot accomplish much|成语用法|班长想改善学习风气，但没有同学配合，实在_____。|D
孤注一掷|把全部力量或资本押上去冒险，以求成功。|to stake everything on one risky attempt|成语用法|公司资金不足，他却决定_____，把所有资金投进一个项目。|D
寡不敌众|人少的一方抵挡不住人多的一方。|to be outnumbered and unable to resist|成语用法|他一个人面对十名对手，最终因_____而败下阵来。|D
光明正大|胸怀坦白，言行正派。|open and aboveboard; honourable|成语用法|他做事一向_____，从不在背后耍手段。|B
裹足不前|因害怕或顾虑而停步不前。|to hesitate and refuse to move forward|成语用法|面对挑战，我们不能因为害怕失败就_____。|B
海底捞针|比喻极难找到。|like looking for a needle in the sea|成语用法|在人山人海的会场找一枚小戒指，简直像_____。|C
骇人听闻|使人听了非常震惊。|shocking; appalling|成语用法|新闻报道了一起_____的虐待案件，社会一片哗然。|C
害群之马|比喻危害集体的人。|a harmful member of a group; black sheep|成语用法|这名员工多次收受贿赂，成了公司里的_____。|B
饱经风霜|形容经历过许多艰难困苦。|to have experienced many hardships; weather-beaten|成语用法|那位老船员一脸沧桑，看得出他_____，经历过不少风浪。|A
里程碑|比喻发展过程中具有重要意义的事件或成就。|a milestone|成语用法|新地铁线正式通车，成为我国公共交通发展的重要_____。|A
赞不绝口|不停地称赞，形容非常赞赏。|to praise continuously; full of praise|成语用法|大家尝了她做的点心后都_____，一致说非常好吃。|B
不偏不倚|不偏向任何一方，表示公正；也可指正好处在中间。|impartial; unbiased|成语用法|裁判处理双方争议时_____，因此大家都接受结果。|B
一帆风顺|比喻事情进行顺利，没有阻碍。|smooth sailing; everything goes smoothly|成语用法|创业不可能总是_____，遇到困难也要坚持。|A
开卷有益|打开书本阅读就会有收获，指读书有好处。|reading is beneficial|成语用法|与其一直刷短视频，不如多读几本好书，毕竟_____。|C
人人皆晓|人人都知道。|known to everyone|成语用法|这位运动员多次为国争光，如今已是_____的人物。|B
慢条斯理|形容说话做事慢而有条理，不慌不忙。|slow and methodical; unhurried|成语用法|大家都急着出发，他却仍_____地整理行李。|B
安然无恙|平安无事，没有受到损害。|safe and sound; unharmed|成语用法|地震过后，家人得知在当地工作的哥哥_____，才终于放心。|A
一马平川|形容地势平坦开阔。|a wide stretch of flat land|成语用法|山脚下地势_____，很适合建设大型农场。|D
全力以赴|把全部力量投入进去。|to go all out; make every effort|成语用法|为了准备决赛，队员们决定_____，争取发挥最佳水平。|A`,'idiom');
const DATA={vocab:[],idiom:IDIOM};
