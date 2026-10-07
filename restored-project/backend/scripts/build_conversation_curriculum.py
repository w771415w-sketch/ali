#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import json, hashlib, random, sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))

TOPICS_EXTENDED=[
('training_success','كيف تقيس نجاح تدريب ALI؟','قارن validation loss والمقاييس الثابتة مع baseline، ثم نفّذ اختبارات regression قبل ترقية النموذج.'),
('continuous_learning','كيف يضيف ALI محادثة جديدة إلى التعلم المستمر؟','يسجل المحادثة بعد التنظيف والـdedup، يستخدمها فورًا عبر الذاكرة، ثم يضيفها إلى Dataset incremental مرة واحدة قبل دورة تدريب وتقييم جديدة.'),
('response_quality','كيف يمنع ALI عرض إجابة مولدة غير موثوقة؟','يمرر الناتج عبر اختبارات جودة اللغة والتكرار والبنية، وإذا فشل يستخدم معرفة موثوقة أو ذاكرة مناسبة بدل تقديم النص المنهار كحقيقة.'),
]
TOPICS=[
('project_inspect','حلل لي مشروعًا قبل التعديل.','ابدأ بجرد الملفات ونقطة الدخول والاعتماديات ومسار التشغيل والاختبارات، ثم سجّل المخاطر قبل اقتراح أي تعديل.'),
('safe_change','كيف تعدل مشروعًا دون كسره؟','اقرأ السياق أولًا، خذ snapshot، ضع خطة صغيرة، طبّقها، شغّل الاختبارات المركزة ثم اختبارات regression وتحقق من الناتج.'),
('test_failure','ماذا تفعل إذا فشل اختبار بعد تعديل؟','حدد أول فشل قابل للتفسير، تتبع السبب الجذري، أصلحه، أعد الاختبار المركز ثم المجموعة الكاملة قبل اعتبار التعديل ناجحًا.'),
('rollback','متى تستخدم rollback؟','استخدم rollback عندما يفشل التحقق أو يظهر regression أو فساد غير مقصود، مع إبقاء النسخة السابقة المعتمدة دون تغيير.'),
('new_project','كيف تنشئ مشروعًا جديدًا؟','حدد المتطلبات، اختر بنية بسيطة، أنشئ الملفات الأساسية والاختبارات، شغّل المشروع ثم وثّق طريقة التشغيل.'),
('python','كيف تحسن برنامج Python؟','قس الأداء والاختبارات أولًا، أصلح أكبر عنق زجاجة مؤكد، حافظ على واجهات المشروع، ثم أعد الاختبارات قبل الانتقال.'),
('sqlite','كيف تتعامل مع SQLite في مشروع محلي؟','استخدم migrations بسيطة، معاملات واضحة، فهارس مناسبة، ونسخة احتياطية قبل تغييرات المخطط المهمة.'),
('git','كيف تستخدم Git أثناء تطوير المشروع؟','افحص status وdiff، اجعل التغييرات صغيرة وقابلة للمراجعة، ثم اختبر قبل commit واضح يصف التغيير الحقيقي.'),
('rag','ما الفرق بين RAG والتدريب؟','RAG يضيف المعرفة وقت الاستدعاء من مصادر قابلة للتحديث، بينما التدريب يغيّر الأوزان ويحتاج Dataset وتقييمًا وإصدارًا جديدًا.'),
('web_research','كيف تحفظ معلومة من الإنترنت؟','احفظ الرابط والعنوان وتاريخ الالتقاط والنص أو المقتطف، افحص المصدر، ثم خزّنها في Knowledge Base قبل التفكير في التدريب.'),
('memory','كيف تتعلم ALI من محادثة جديدة؟','يحفظ الزوج بعد التنظيف وتسجيل المصدر ويستطيع استرجاعه فورًا، ثم يدخل Dataset جديدًا فقط إذا كان عالي الجودة وغير مكرر.'),
('dedup','كيف تمنع تكرار التدريب؟','احسب hash ثابتًا للعينات وDataset الكامل، وسجل آخر هوية تم تدريبها، وأنشئ Candidate فقط عند وجود هويات جديدة.'),
('checkpoint','ماذا يحتوي checkpoint حقيقي؟','يحفظ الأوزان وحالة optimizer وscheduler وRNG وإعدادات التدريب والعدادات والمقاييس اللازمة للاستئناف.'),
('resume','كيف يستأنف ALI التدريب؟','يحمل آخر checkpoint موثوق، يستعيد النموذج والoptimizer وscheduler وRNG ثم يكمل من الخطوة المسجلة بدل البدء من الصفر.'),
('gguf','ما هو GGUF في ALI؟','هو snapshot للاستدلال من أوزان ALI المصدّرة، وليس قاعدة بيانات لإضافة معلومات جديدة مباشرة إلى الملف نفسه.'),
('quant','كيف تضغط النموذج؟','بعد تقييم checkpoint صدّر نسخة استدلال مناسبة ثم طبّق quantization مدعومة مثل Q4 أو Q5 أو Q8 عند توفر الأداة، واحتفظ بالأصل.'),
('cpu','كيف تسرع التدريب على CPU؟','استخدم عدد خيوط مناسب، SDPA، batch صغير مع gradient accumulation، sequence قصيرة، checkpointing وتجنب تحميل بيانات مكرر.'),
('2gb','كيف تضبط ALI لجهاز 2GB VRAM؟','اجعل batch=1، استخدم gradient accumulation وcheckpointing وسياقًا متحفظًا، واسمح بالتحول إلى CPU إذا لم تكفِ VRAM.'),
('ram','كيف تستفيد من 32GB RAM؟','استخدم RAM للتخزين المؤقت، فهرسة المعرفة، DataLoader بسيط وoffload محسوب، مع حد أعلى يمنع امتلاء الذاكرة.'),
('multimodal','كيف يتعامل ALI مع الصور والصوت والفيديو؟','يستخرج تمثيلًا عصبيًا محليًا للوسيط ثم يمرره عبر projector إلى مساحة ALI، مع حفظ المصدر وعدم خلط ملفات الوسائط عشوائيًا مع نص التدريب.'),
('pdf','كيف يتعلم من PDF؟','استخرج النص والصفحات والجداول عند الإمكان، احتفظ برقم الصفحة والمصدر، ثم افصل المعرفة القابلة للبحث عن أمثلة التدريب.'),
('archive','كيف تتعامل مع ZIP أو أرشيف؟','تحقق من المسار ونوع الملف والحجم، فكّه داخل مجلد downloads/extracted آمن، ثم افحص المحتويات recursively.'),
('security','ما أهم قواعد أمان الوكيل؟','قيّد المسارات والأوامر، استخدم allowlist، اطلب تأكيدًا للعمليات الحساسة، وسجّل audit trail ولا تسرب الأسرار.'),
('tool','متى يستخدم ALI الأدوات؟','يستخدم الأداة عندما يحتاج دليلًا أو فعلًا خارج النموذج، وينتظر نتيجة حقيقية ثم يبني الإجابة منها.'),
('tool_call','كيف يتعلم tool calling؟','تدرّب المحادثات على مخططات الأدوات وأمثلة اختيار الأداة والوسائط، ثم قيّم صحة JSON والتنفيذ قبل الترقية.'),
('agent','كيف يعمل وكيل المشروع؟','يفحص ثم يخطط ثم يأخذ snapshot ثم يطبق ثم يختبر ثم يتحقق ثم يراجع قبل إغلاق المهمة.'),
('skills','ما فائدة skills؟','هي وصفات قابلة للتحميل تحدد طريقة حل نوع من المهام وأدواتها وشروط النجاح، وتبقى منفصلة عن النواة.'),
('plugins','كيف تعمل plugins؟','تُسجّل كإضافات اختيارية بصلاحيات واضحة ومخطط إدخال وإخراج، ولا تعمل تلقائيًا دون تفعيلها.'),
('mcp','كيف تستخدم MCP؟','يُشغّل خادم MCP اختياريًا عبر قناة محلية مضبوطة، وتُكتشف الأدوات منه ثم تمر كل عملية عبر صلاحيات ALI.'),
('offline','هل يعمل ALI بدون إنترنت؟','نعم في مسار المعرفة المحلية والتدريب والاستدلال، أما البحث الشبكي فيبقى طبقة اختيارية لا يعتمد عليها التشغيل الأساسي.'),
('uncertainty','ماذا تفعل عندما لا تعرف الإجابة؟','لا تخمّن كحقيقة؛ اذكر حدود الأدلة واستعمل Knowledge أو البحث أو اطلب معلومة إضافية عندما تكون ضرورية.'),
('conversation','كيف يجب أن يرد ALI على المستخدم؟','يحافظ على لغة المستخدم، يجيب مباشرة، يوضح الخطوات عند الحاجة، ويذكر عدم اليقين والمصادر عندما تكون مهمة.'),
('dataset','كيف تبني Dataset للمحادثات؟','نظف الرسائل، حافظ على ترتيب الأدوار، احذف الأسرار والتكرار، افصل train/validation/test ثم افحص الجودة قبل التدريب.'),
('curriculum','ما فائدة Curriculum Learning؟','يجعل التدريب يمر من أمثلة أسهل إلى أمثلة أصعب وفق درجة محددة بدل خلط كل الصعوبات من البداية.'),
('evaluation','كيف تعرف أن النموذج تحسن؟','قارن baseline وcandidate على validation وbenchmarks واختبارات regression ولا تعتمد على training loss وحده.'),
('arabic','كيف تقيم العربية؟','استخدم أسئلة عربية متنوعة، قياس تطابق اللغة، فهم التعليمات، استرجاع المعرفة، وجودة الأجوبة وعدم اختلاق الأدلة.'),
('english','كيف تقيم الإنجليزية؟','استخدم أسئلة متنوعة في التعليمات والبرمجة والاستدعاء والحوارات وراجع الدقة والوضوح والثبات عبر benchmark ثابت.'),
('new_info','ماذا يحدث عند إدخال معلومات جديدة؟','تُنقّى وتُفهرس وتُسجل بهوية مصدر، ثم تستخدم فورًا في RAG، ولا تدخل الأوزان إلا عبر دورة Dataset وتدريب وتقييم جديدة.'),
('no_dup_gguf','كيف تمنع GGUF المكرر؟','اربط GGUF بهوية checkpoint وDataset وquantization، ولا تصدر ملفًا جديدًا إذا كانت الهوية مطابقة لإصدار موجود.'),
('download','أين تحفظ الملفات التي ينزلها ALI؟','ضعها في downloads مع metadata المصدر والوقت وhash، وافحصها قبل فكها أو إدخالها في المعرفة.'),
('libraries','كيف تدير المكتبات؟','افصل المكتبات المحلية عن المشروع، سجل الإصدار والمصدر، واستخدم بيئة افتراضية حتى لا تلوث النظام.'),
('preview','متى تستخدم Preview Pane؟','عند الحاجة لمعاينة HTML أو صورة أو ملف إخراج للمشروع بعد التعديل، مع إبقاء المعاينة منفصلة عن صلاحيات التنفيذ.'),
('web_ui','كيف تبني Web UI محليًا؟','استخدم API محليًا على localhost وواجهة ثابتة، واجعل الواجهة تتصل بالمحرك المحلي بدل إرسال البيانات خارجيًا.'),
('tui','ما فائدة TUI؟','توفر تحكمًا سريعًا من الطرفية في الأنظمة التي لا تحتاج واجهة رسومية كاملة، مع عرض الحالة والسجل والتدريب.'),
('logs','ما الذي يجب تسجيله؟','سجل الوقت والمهمة والأداة والنتيجة والمدة وحالة الموارد والمصدر مع منع كتابة الأسرار أو الرموز السرية إلى السجل.'),
('errors','كيف يتعامل النظام مع خطأ داخلي؟','احتفظ بالنسخة السابقة، سجل traceback محليًا، اعرض رسالة مفهومة، ثم أعد المحاولة فقط إذا كانت السياسة تسمح بذلك.'),
('self_dev','كيف يطور ALI نفسه؟','لا يعدل النواة عشوائيًا؛ يقترح تغييرًا، ينشئ branch أو snapshot، يشغّل الاختبارات، ثم يقبل النسخة فقط إذا اجتازت بوابة التحقق.'),
('project_graph','كيف يفهم علاقات المشروع؟','يبني فهرسًا للملفات والرموز والاختبارات والمداخل والاعتماديات ثم يستخدم هذه العلاقات عند التخطيط للتغيير.'),
('code_search','كيف يجد الملف المرتبط بمشكلة؟','يستخدم فهرس أسماء الملفات ونصوصها والرموز ثم يقرأ السياق المحيط قبل اختيار موضع التعديل.'),
('performance','كيف تقيس سرعة ALI؟','سجل tokens/sec وزمن الاستجابة واستخدام CPU/RAM/VRAM وحجم السياق ومعدل الأخطاء لكل إصدار.'),
]

TOPICS = TOPICS + TOPICS_EXTENDED

TEMPLATES_AR=[
    'كيف يتم تنفيذ {}؟', 'اشرح لي طريقة {}.', 'أريد من ALI أن ينفذ {}؛ كيف يفعل ذلك؟',
    'ما الخطوات العملية لتنفيذ {}؟', 'كيف أتعامل مع مشكلة مرتبطة بـ{}؟', 'متى يكون مناسبًا تنفيذ عملية {}؟',
    'ما الذي يجب فحصه قبل تنفيذ {}؟', 'كيف يتحقق ALI من نجاح عملية {}؟', 'ماذا يفعل ALI أثناء عملية {}؟', 'كيف يمكن تحسين عملية {}؟'
]
TEMPLATES_EN=[
    'What is the correct way to {}?', 'Explain how to {}.', 'I want ALI to {}; how should it do that?',
    'What are the practical steps to {}?', 'How should I handle a case where I need to {}?', 'When is it appropriate to {}?',
    'What should be checked before I {}?', 'How does ALI verify successful execution of {}?', 'What should ALI do if it needs to {}?', 'How can the approach to {} be improved?'
]
AR_ACTIONS={
'project_inspect':'تحليل المشروع قبل التعديل','safe_change':'تعديل المشروع دون كسره','test_failure':'التعامل مع فشل اختبار بعد تعديل','rollback':'استخدام rollback عند الحاجة','new_project':'إنشاء مشروع جديد','python':'تحسين برنامج Python','sqlite':'التعامل مع SQLite في مشروع محلي','git':'استخدام Git أثناء تطوير المشروع','rag':'فهم الفرق بين RAG والتدريب','web_research':'حفظ معلومة من الإنترنت','memory':'تعلم ALI من محادثة جديدة','dedup':'منع تكرار بيانات التدريب','checkpoint':'فهم ما يحتويه checkpoint الحقيقي','resume':'استئناف تدريب ALI','gguf':'استخدام GGUF في ALI','quant':'ضغط النموذج بالـquantization','cpu':'تسريع التدريب على CPU','2gb':'ضبط ALI لجهاز بذاكرة VRAM قدرها 2GB','ram':'الاستفادة من 32GB RAM','multimodal':'تعامل ALI مع الصور والصوت والفيديو','pdf':'تعلم ALI من ملف PDF','archive':'التعامل مع ملفات ZIP والأرشيفات','security':'تأمين الوكيل وأدواته','tool':'تحديد متى يستخدم ALI الأدوات','tool_call':'تعلم ALI لاستدعاء الأدوات','agent':'تشغيل دورة عمل وكيل المشروع','skills':'استخدام skills','plugins':'استخدام plugins','mcp':'استخدام MCP','offline':'تشغيل ALI دون إنترنت','uncertainty':'التعامل مع الأسئلة التي لا يعرفها','conversation':'الرد على المستخدم بطريقة صحيحة','dataset':'بناء Dataset للمحادثات','curriculum':'استخدام Curriculum Learning','evaluation':'قياس تحسن النموذج','arabic':'تقييم جودة العربية','english':'تقييم جودة الإنجليزية','new_info':'إضافة معلومات جديدة','no_dup_gguf':'منع تكرار ملفات GGUF','download':'حفظ الملفات التي ينزلها ALI','libraries':'إدارة المكتبات المحلية','preview':'استخدام Preview Pane','web_ui':'بناء Web UI محلي','tui':'استخدام TUI','logs':'تسجيل العمليات والسجلات بشكل آمن','errors':'التعامل مع خطأ داخلي','self_dev':'تطوير ALI لنفسه بشكل آمن','project_graph':'فهم علاقات المشروع','code_search':'العثور على الملف المرتبط بمشكلة','performance':'قياس سرعة وأداء ALI','training_success':'قياس نجاح تدريب ALI','continuous_learning':'إضافة محادثة جديدة إلى التعلم المستمر','response_quality':'منع عرض إجابة مولدة غير موثوقة'
}

def build():
    out=[]; seen=set()
    for key, ar_answer, en_answer in TOPICS:
        # derive a compact infinitive/phrase from the topic's first clause for prompts
        ar_action=AR_ACTIONS[key]
        en_action={
            'project_inspect':'inspect a project before changing it','safe_change':'modify a project without breaking it','test_failure':'a test fails after a change',
            'rollback':'use rollback','new_project':'create a new project','python':'improve a Python program','sqlite':'handle SQLite in a local project','git':'use Git while developing',
            'rag':'understand RAG versus training','web_research':'store information from the internet','memory':'teach ALI from a new conversation','dedup':'prevent duplicate training',
            'checkpoint':'understand a real checkpoint','resume':'resume ALI training','gguf':'use GGUF in ALI','quant':'quantize the model','cpu':'speed up training on CPU',
            '2gb':'configure ALI for a 2GB VRAM machine','ram':'use 32GB of RAM effectively','multimodal':'handle images, audio and video','pdf':'learn from a PDF','archive':'process ZIP or archive files',
            'security':'secure the agent','tool':'decide when ALI should use tools','tool_call':'learn tool calling','agent':'run the project agent workflow','skills':'use skills','plugins':'use plugins',
            'mcp':'use MCP','offline':'run ALI without internet','uncertainty':'handle unknown questions','conversation':'respond to the user','dataset':'build a conversation dataset','curriculum':'use curriculum learning',
            'evaluation':'measure whether the model improved','arabic':'evaluate Arabic','english':'evaluate English','new_info':'add new information','no_dup_gguf':'prevent duplicate GGUF exports',
            'download':'store downloaded files','libraries':'manage local libraries','preview':'use the preview pane','web_ui':'build a local Web UI','tui':'use the TUI','logs':'log the right information',
            'errors':'handle an internal error','self_dev':'let ALI improve itself safely','project_graph':'understand project relationships','code_search':'find the file related to a problem',
            'performance':'measure ALI performance','training_success':'measure ALI training success','continuous_learning':'add a new conversation to continuous learning','response_quality':'prevent an unreliable generated answer from being shown'
        }[key]
        for i in range(10):
            ar=TEMPLATES_AR[i].format(ar_action)
            en= TEMPLATES_EN[i].format(en_action)
            for lang,prompt,ans in [('ar',ar,ar_answer),('en',en,en_answer)]:
                pair=(prompt,ans)
                h=hashlib.sha256((prompt+'\n'+ans).encode()).hexdigest()
                if h in seen: continue
                seen.add(h)
                out.append({'id':h,'messages':[{'role':'system','content':'You are ALI. Answer in the user language and do not invent evidence.'},{'role':'user','content':prompt},{'role':'assistant','content':ans}], 'metadata':{'topic':key,'language':lang,'source':'curated-curriculum'}})
    random.Random(42).shuffle(out)
    path=ROOT/'data/seed/conversations_curriculum.jsonl'; path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8') as f:
        for r in out:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    # split
    split=ROOT/'data/training/curriculum'; split.mkdir(parents=True,exist_ok=True)
    n=len(out); a=int(n*.8); b=int(n*.9)
    parts={'chat_train':out[:a],'chat_validation':out[a:b],'chat_test':out[b:]}
    for name,rows in parts.items():
        with (split/(name+'.jsonl')).open('w',encoding='utf-8') as f:
            for r in rows:f.write(json.dumps({'id':r['id'],'messages':r['messages'],'text':''.join(f"<|{m['role']}|>\n{m['content']}\n<|eot|>\n" for m in r['messages'])},ensure_ascii=False)+'\n')
    print(json.dumps({'total':n,'train':a,'validation':b-a,'test':n-b,'path':str(path)},ensure_ascii=False,indent=2))
if __name__=='__main__':build()
