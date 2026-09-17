const parseBank=(raw,kind)=>raw.trim().split('\n').filter(Boolean).map(line=>{const [term,zh,en,coll,context]=line.split('|');return{term,zh,en,coll,context,kind}});
const VOCAB=parseBank(`秉持|坚持、保持某种态度或原则。|to uphold; to adhere to|秉持原则 / 秉持信念|
步伐|行走时的脚步；也比喻事情进行的速度或节奏。|pace; steps|加快步伐 / 跟上步伐|
赋予|给予某人或某事物任务、权利、意义、特点等。|to give; to grant; to endow|赋予使命 / 赋予意义|
携手|比喻一起合作做某事。|to join hands; to collaborate|携手合作 / 携手前进|
可谓|可以说。|it may be said; it could be said|可谓成功 / 可谓难得|
岛屿|岛的总称。|islands|大小岛屿|
海峡|两块陆地之间、连接两片较大水域的狭窄水道。|strait|穿过海峡 / 海峡两岸|
历史|过去发生的事情和发展过程。|history|悠久历史 / 历史发展|
钱币|货币，尤其指金属制成的钱。|coin; currency|古代钱币 / 收藏钱币|
初来乍到|刚到一个地方不久，对当地情况还不熟悉。|newly arrived|初来乍到，对环境不熟|
区域|一定范围的地区。|area; region; district|这个区域 / 城市区域|
啧啧称奇|因惊奇或赞叹而不断称赞。|to express amazement or admiration|令人啧啧称奇|
汇集|把来自不同来源或方向的人或事物集中到一起。|to gather; to collect|汇集人才 / 汇集资料|
海纳百川|比喻胸怀宽广，能包容各种不同的人、意见或事物。|to be broad-minded and tolerant of diversity|海纳百川的胸怀|
发芽|种子开始长出芽；也比喻想法或事物开始发展。|to germinate; to sprout|种子发芽 / 梦想发芽|
兼容并蓄|把不同的内容、观点或事物都吸收、包容进来。|to be inclusive; to embrace different ideas|兼容并蓄的态度|
辉煌|光彩夺目；也形容成就非常出色。|splendid; glorious|辉煌成就 / 辉煌业绩|
得天独厚|所处环境或具有的条件特别优越。|to enjoy exceptional advantages|得天独厚的条件|
求同存异|寻找共同点，同时保留不同意见。|to seek common ground while reserving differences|求同存异的原则|
无远弗届|不管多远都能到达；也形容影响或传播范围很广。|to reach everywhere, however far|影响无远弗届|
真伪|真假。|true or false; authenticity|辨别真伪|有些商品越来越难辨别真伪了。
询问|向别人打听情况或征求意见。|to ask; to inquire|询问情况 / 询问意见|
人云亦云|别人说什么，自己就跟着说什么，形容没有主见。|to echo what others say|不要人云亦云|
免疫|身体抵抗病菌、病毒等侵害的能力；也可指不容易受到某种影响。|immunity; to be immune to|提高免疫力 / 对广告免疫|
凝聚力|使一个群体团结在一起的力量。|cohesion; cohesiveness|团队凝聚力|
陷阱|比喻使人受骗上当的圈套。|trap|掉入陷阱 / 网络陷阱|
砍|用刀斧等用力劈。|to chop; to cut|砍树 / 砍伐|
丝绸|用蚕丝织成的布料。|silk; silk cloth|丝绸衣服 / 丝绸之路|
奢侈品|不是生活必需、价格较高的高级消费品。|luxury goods|购买奢侈品|
陆地|地球表面没有被海水覆盖的部分。|land; dry land|回到陆地 / 陆地面积|
仪式|按一定程序进行的典礼或活动。|ceremony; ritual|举行仪式 / 开幕仪式|
枢纽|重要的地点或事物的关键连接处。|hub; key junction|交通枢纽 / 重要枢纽|这里将成为这座城市重要的交通枢纽。
港口|船只停靠、装卸货物和旅客上下船的地方。|port; harbour|港口城市 / 进入港口|
勾勒|画出大概轮廓；也比喻用简短文字写出大概情况。|to outline; to sketch|勾勒轮廓 / 勾勒情景|
高瞻远瞩|比喻眼光远大，看得长远。|to be far-sighted|高瞻远瞩的眼光|
政府|管理国家或地区的机构。|government|政府部门 / 政府政策|
小贩|摆摊售卖食物或商品的人。|hawker|小贩中心 / 流动小贩|
诊疗所|给病人看病和治疗的地方。|clinic|到诊疗所看病|
经济|与生产、买卖和消费有关的活动。|economy|经济发展 / 经济状况|
屡次|一次又一次，多次。|repeatedly; time and again|屡次失败 / 屡次提醒|
简陋|房屋、设备等很简单，不完善。|simple and crude; poorly equipped|设备简陋 / 环境简陋|
开辟|开拓新的地方、道路或领域；也可指创立、开办。|to open up; to develop|开辟道路 / 开辟新领域|
宗教|关于信仰神灵等的一套思想和活动。|religion|宗教信仰 / 宗教活动|
综合|把不同但有关联的内容合在一起考虑或处理。|to combine; to integrate|综合考虑 / 综合能力|
富裕|钱财充足，生活条件好。|wealthy; well-off|生活富裕 / 富裕家庭|
变迁|随着时间发生变化。|change; transition|时代变迁 / 社会变迁|
驰名|名声传播得很远。|famous; renowned|驰名中外 / 驰名海外|
障碍|阻挡前进或发展的东西。|obstacle; barrier|克服障碍 / 沟通障碍|
荣誉|因成就或表现而得到的光荣名声或称号。|honour|获得荣誉 / 集体荣誉|
接纳|接受并愿意让对方成为其中的一部分。|to accept; to welcome|接纳意见 / 接纳新成员|
接触|碰到，或与人、事物发生联系。|to come into contact with|接触社会 / 接触新事物|
翠绿|鲜亮的绿色。|bright green|翠绿的树叶|
心旷神怡|心情舒畅，精神愉快。|to feel relaxed and refreshed|令人心旷神怡|
樟宜|新加坡东部的一个地区。|Changi|樟宜机场 / 樟宜海滨|
耸立|高高地直立着。|to stand tall|高楼耸立 / 山峰耸立|
欣赏|观看并感受其中的美好。|to appreciate; to admire|欣赏美景 / 欣赏作品|
粗糙|表面不光滑；也可形容做工不精细。|rough|表面粗糙 / 做工粗糙|
婆娑|枝叶等轻柔地摇动的样子。|to sway gracefully|树影婆娑 / 枝叶婆娑|
翱翔|在高空自由地飞翔。|to soar|展翅翱翔 / 在天空翱翔|
同甘共苦|一起分享快乐，也一起承受困难。|to share joys and hardships|与伙伴同甘共苦|
茁壮|健康而强壮地成长。|to grow strong and healthy|茁壮成长|
叮嘱|再三提醒、嘱咐别人要注意或做好某事。|to repeatedly remind or instruct|再三叮嘱 / 叮嘱孩子|
叮咛|反复而关心地嘱咐、提醒。|to remind or advise repeatedly|细心叮咛 / 临行叮咛|
烦躁|心情不安、焦虑或容易发怒。|irritable; restless|心情烦躁 / 感到烦躁|
曝晒|长时间暴露在强烈阳光下晒。|to expose to strong sunlight|在烈日下曝晒|
合拢|把原来分开或张开的东西合到一起。|to close; to bring together|双手合拢 / 花瓣合拢|
林荫大道|两旁种有树木的大路。|tree-lined avenue; boulevard|宽阔的林荫大道|
寻找|为了找到某人或某物而去找。|to look for; to search for|寻找答案 / 寻找机会|
失智症|会影响记忆、思考和日常生活能力的一类疾病。|dementia|患失智症 / 失智症患者|
流逝|像流水一样不断过去，常用来形容时间过去。|to pass; to slip away|时间流逝 / 岁月流逝|
嬉戏|玩耍、游戏。|to play; to frolic|孩子嬉戏 / 水中嬉戏|
温馨|温暖、舒适而亲切。|warm and cosy|温馨的家庭 / 温馨气氛|
患|生某种病。|to suffer from; to contract an illness|患病 / 患重病|
妻子|男子的配偶。|wife|他的妻子|
惬意|感到舒适、满意、自在。|comfortable; contented; pleasant|生活惬意 / 感到惬意|
魂不守舍|形容心神不定，无法专心。|absent-minded; distracted|一整天魂不守舍|
反驳|提出理由，否定别人的意见。|to refute; to rebut|反驳观点 / 反驳对方|
拘束|感到不自在、不自然，放不开。|constrained; uncomfortable|感到拘束 / 不必拘束|
自卑|觉得自己比不上别人而看轻自己。|to feel inferior; low self-esteem|感到自卑 / 克服自卑|
羡慕|希望自己也能拥有别人有的好处或条件。|to envy; to admire|羡慕别人 / 令人羡慕|
闪烁其词|说话吞吞吐吐，故意回避重点或不肯说出真相。|evasive; to dodge the issue|回答时闪烁其词|
诱惑|吸引或引诱人，使人很想去做某事；有时指引诱人做不好的事。|temptation; to tempt; to lure|抵抗诱惑 / 金钱诱惑|
茫然|不明白、不知所措的样子。|at a loss; blankly|一脸茫然 / 感到茫然|
睡眠|睡觉的状态和过程。|sleep|充足睡眠 / 睡眠不足|
霸道|蛮横强势，不讲道理。|bossy; domineering|作风霸道 / 太霸道|
逼|施加压力，强迫别人做某事。|to force; to compel|逼他道歉 / 被逼无奈|
符合|与要求、标准或实际情况一致。|to conform to; to be in line with|符合要求 / 符合标准|
怄气|跟人闹别扭，或自己生闷气。|to sulk|和别人怄气|
烹饪|做饭做菜，加工食物。|cooking; culinary arts|学习烹饪 / 烹饪技巧|
嫌|对某人或某事不满意，觉得不好或不够好。|to dislike; to find fault with|嫌太贵 / 嫌麻烦|
毅力|坚强而持久的意志。|perseverance; willpower|有毅力 / 靠毅力坚持|
恐怖|令人极度害怕或不安。|terrifying; horrifying|恐怖故事 / 恐怖气氛|
憋|勉强忍住，不让情绪、话语等表达出来。|to hold back; to bottle up|憋住眼泪 / 憋在心里|
委婉|说话比较含蓄，不直接、不生硬。|indirect; tactful; euphemistic|说法委婉 / 委婉表达|
吼|大声叫喊。|to yell; to roar|大吼一声 / 冲着人吼|
吭声|出声说话。|to make a sound; to speak|一声不吭 / 不敢吭声|
走廊|连接房间的狭长通道。|corridor|学校走廊 / 走廊尽头|
诡异|奇怪、不寻常，让人觉得不安。|strange; eerie|诡异的气氛 / 表情诡异|
蜷缩|把身体缩成一团。|to curl up; to cower|蜷缩在角落|
通宵|整夜不睡或整夜持续进行。|all night; overnight|通宵学习 / 通宵工作|
惊悚|令人感到害怕、紧张。|frightening; horrifying|惊悚电影 / 惊悚情节|
脖子|头和身体相连的部分。|neck|伸长脖子 / 脖子酸痛|
掩饰|故意隐藏真实的情感、事实或缺点。|to hide; to cover up|掩饰紧张 / 掩饰错误|
嘈杂|声音多而乱，让人觉得吵。|noisy|环境嘈杂 / 人声嘈杂|
局促|空间狭窄；时间不够宽裕；也可形容人拘谨、不自在。|cramped; constrained; uneasy|空间局促 / 神情局促|
沮丧|因失败或挫折而失望、灰心。|discouraged; dejected|感到沮丧 / 神情沮丧|
睿智|有智慧、有远见。|wise; insightful|睿智的判断 / 睿智老人|
瞥|很快地看一眼。|to glance|瞥了一眼 / 偷偷一瞥|
炙|用火烤。|to roast; to grill|炙烤 / 炙热|
社交媒体|让人们在网上交流、分享内容的平台。|social media|使用社交媒体 / 社交媒体平台|`,'vocab');
const IDIOM=parseBank(`好逸恶劳|贪图安逸，厌恶劳动。|to love ease and dislike work|成语用法|家杰_____，总是贪图享受，希望别人能帮他把工作做完。
鹤立鸡群|比喻一个人的才能或仪表特别出众。|to stand out from the crowd|成语用法|宴会上，她那浑身雪白的打扮，在红男绿女之中就有_____之感。
狐假虎威|比喻依仗别人的势力去欺压他人。|to bully others by relying on powerful connections|成语用法|他仗着姐夫是公司的董事，便经常_____，欺负同事。
囫囵吞枣|比喻学习时不加分析，不求甚解地笼统接受。|to swallow information without understanding it|成语用法|对于别人的意见，需要加以分析，不可以_____。
胡作非为|不顾法纪或舆论，毫无顾忌地做坏事。|to behave lawlessly; to do evil|成语用法|这些不良少年经常在这一带_____，干扰居民生活。
花言巧语|指用来骗人的虚假而动听的话。|sweet talk; deceptive flattering words|成语用法|在他_____的哄骗下，世杰信以为真，向他买了那批仿制的古董。
画龙点睛|比喻在关键处用几句话点明实质，使内容更生动有力。|to add the vital finishing touch|成语用法|写作文时，适当引用一些诗文名句，可以收到_____的效果。
画蛇添足|比喻做了多余的事，反而不恰当。|to do something unnecessary and spoil it|成语用法|明华已经把这里布置成古代战场，你却放了一辆古董车在中央，简直是_____。
诲人不倦|教导别人特别有耐心，从不厌倦。|to teach patiently and tirelessly|成语用法|_____的陈老师，深得学生的爱戴和赞许。
浑水摸鱼|比喻趁混乱的时候从中取得利益。|to fish in troubled waters; to take advantage of confusion|成语用法|火灾发生时，竟有人_____偷取灾民财物，真让人心寒。
豁然开朗|比喻突然明白了某个道理。|to suddenly understand; everything becomes clear|成语用法|一旦变换看问题的角度，你会_____，知道该怎么做了。
家喻户晓|家家户户都知道，形容人人皆知。|well-known; a household name|成语用法|这家肉干店是_____的，每年新年店前总是大排长龙。
见仁见智|对同一个问题，不同的人有不同的看法。|different people have different views|成语用法|这部电影的好坏_____，有人说好看，也有人说不喜欢。
见义勇为|看到正义的事，就勇敢地去做。|to act courageously for a just cause|成语用法|他看到一名学生被人欺负，马上上前制止，真是个_____的青年。
捷足先登|比喻行动快的人先达到目的或先得到想要的东西。|the early bird gets there first|成语用法|丽美原以为自己能抢先买到限量版手机，谁知别人已_____，买下了最后一台。
金玉良言|比喻可贵而有价值的劝告。|invaluable advice|成语用法|母亲所说的话句句都是_____，你要认真听取。
锦上添花|比喻使已经很好的事物变得更好。|to add beauty to something already good|成语用法|真正的朋友不只会_____，更会在你困难时雪中送炭。
近朱者赤，近墨者黑|比喻环境和身边的人会影响一个人。|people are influenced by the company they keep|成语用法|所谓“_____”，因此交友时我们应该更加谨慎。
惊弓之鸟|比喻受过惊吓后，遇到一点动静就非常害怕的人。|a badly frightened person; easily alarmed|成语用法|很多经历过战争的人，一听到枪声，就像_____一样慌张起来。
井井有条|形容做事、安排等很有条理，整齐有序。|well-organised; methodical|成语用法|他做事细心，每件事都安排得_____。
咎由自取|灾祸或后果是自己造成的，怪不得别人。|to have only oneself to blame|成语用法|我已经多次警告你别太信任他，你却不听，现在被骗了，也是_____。
居安思危|处在平安环境中，也想到可能出现危险，并预先准备。|to be prepared for danger even in safe times|成语用法|生活环境虽然安逸，我们仍要_____，预先做好应对危机的准备。
举足轻重|形容地位重要，一举一动都会产生很大影响。|to play a key role; to carry great weight|成语用法|家强是篮球队的射手，在这场比赛中_____，是输赢的关键。
开门见山|比喻说话或写文章直截了当地进入正题。|to get straight to the point|成语用法|我们是多年的好朋友，有什么事就_____地说，不必拐弯抹角。
开源节流|比喻增加收入，同时节省开支。|to increase income and cut expenses|成语用法|我们的公司才刚起步，因此更应该_____，巩固经济基础。
慷慨解囊|形容很大方地在经济上帮助别人。|to help someone generously with money|成语用法|看到这些需要帮助的孩子，大家纷纷_____相助。
口若悬河|形容口才很好，说起话来滔滔不绝。|eloquent; to speak fluently and continuously|成语用法|他口才很好，每次发表意见都_____，滔滔不绝。
口是心非|嘴上说的和心里想的不一样。|to say one thing but mean another|成语用法|他嘴上说赞成这个计划，心里其实非常反对，真是_____。
扣人心弦|形容事物非常吸引人、激动人心。|thrilling; gripping|成语用法|这部电影的情节_____，看完后令人回味无穷。
苦口婆心|形容善意而又耐心地劝导。|to advise earnestly and patiently|成语用法|在老师和父母_____的劝导下，他终于决定改过自新。
滥竽充数|比喻没有本领的人冒充有本领，或次货冒充好货。|to pass oneself off as competent; to make up the numbers|成语用法|他的演奏水平不高，却_____，参加乐队演出。
狼狈为奸|比喻坏人互相勾结，一起做坏事。|villains collude together|成语用法|这两个罪犯臭味相投，_____，干了许多坏事。
礼尚往来|在礼节上讲究有来有往；也指用相应的态度或做法回报对方。|courtesy calls for reciprocity|成语用法|去年他们热情接待我们，下周他们来我校，我们也应该好好接待，这是_____嘛！
理直气壮|理由充分、正当，所以说话很有气势。|to speak boldly and confidently with good reason|成语用法|既然你认为自己没做错，就应该_____，坚持自己的立场。
力不从心|心里想做，但能力或力量不够。|to be willing but unable; strength falls short|成语用法|王先生经验丰富，可如今年事已高，身体虚弱，_____，无法再到商海打拼。
立竿见影|比喻立刻见到效果。|to have an immediate effect|成语用法|这种药十分灵验，能_____，疼痛很快就消失。
良药苦口|比喻对人有帮助的劝告，往往听起来不舒服，却是为了他好。|good advice may be unpleasant to hear but beneficial|成语用法|父母师长的指导虽然严厉了些，但_____，他们也是希望你能有所进步。
了如指掌|形容对某件事非常熟悉、非常了解。|to know something very well; like the back of one's hand|成语用法|我对华人传统文化习俗_____，做你的旅游向导最适合不过了。
淋漓尽致|形容把感情、意思或特点表现得非常充分、透彻。|to express or display something to the fullest|成语用法|电视小品《孔乙己》把鲁迅作品中含泪的幽默表现得_____。
令人发指|形容某种行为恶劣到了让人非常愤怒的程度。|outrageous; horrifyingly cruel|成语用法|为了自身利益骗取老人家的血汗钱，这样的行为简直_____。
路不拾遗|形容社会风气很好，人们诚实守法，路上失物也没人据为己有。|a society where lost property is left untouched|成语用法|这个国家民风淳朴，_____，百姓安居乐业。
屡见不鲜|多次见过，已经不觉得新奇。|a common occurrence; nothing new|成语用法|类似的网络骗局如今已经_____，大家要提高警惕。
络绎不绝|形容人、车等来来往往，连续不断。|in an endless stream; coming and going continuously|成语用法|这个医生医术高明，前来求诊的患者_____。
落花流水|常用来形容在战斗或竞争中一方被打得大败。|to be thoroughly defeated|成语用法|由于没有充分准备，我们的球队被对手打得_____。
毛骨悚然|形容感到非常恐惧。|to feel terrified; hair stands on end|成语用法|听了这个恐怖故事后，她感到_____，连回家都要有人陪伴。
毛遂自荐|比喻主动推荐自己担任某项工作。|to volunteer oneself; to recommend oneself|成语用法|在选举班长时，志文_____，老师赞扬他的勇气。
每况愈下|形容情况越来越糟。|to get worse and worse|成语用法|经济不景气，该公司的生意_____，可能马上要裁员了。
面面俱到|形容各方面都照顾得很周全，没有遗漏。|to cover all aspects thoroughly|成语用法|公司新来的经理做事非常细心，各方面都照顾得_____。
面目全非|形容样子改变得很厉害，已经完全不同。|to be changed beyond recognition|成语用法|大火过后，那栋旧屋已经_____，几乎认不出来了。
名列前茅|指名次排在前面。|to rank among the top|成语用法|他的聪慧加上平日用功，使他在考试中_____。
名落孙山|指在考试或选拔中没有被录取。|to fail an examination or selection|成语用法|他上课不专心，又不用功，结果考试成绩公布后_____。
墨守成规|守着旧规矩不肯改变，带有贬义。|to stick rigidly to old rules|成语用法|这间工厂过去因为_____，生产模式落后，最终被迫结束营业。`,'idiom');
const DATA={vocab:VOCAB,idiom:IDIOM};