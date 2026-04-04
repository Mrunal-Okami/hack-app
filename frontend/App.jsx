// Helper to create React components from Lucide icons
const Icon = ({ name, size = 18, ...props }) => {
    React.useEffect(() => {
        if (window.lucide) window.lucide.createIcons();
    }, []);
    return <i data-lucide={name} style={{ width: size, height: size }} {...props}></i>;
};

const Plus = (p) => <Icon name="plus" {...p} />;
const ArrowUp = (p) => <Icon name="arrow-up" {...p} />;
const History = (p) => <Icon name="history" {...p} />;
const Settings = (p) => <Icon name="settings" {...p} />;

function VersatileApp() {
    const [messages, setMessages] = React.useState([
        { role: 'system', content: "Hello! I am Versatile. Paste a claim to analyze truthfulness.", isInitial: true }
    ]);
    const [inputText, setInputText] = React.useState("");
    const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);
    const [isAnalyzing, setIsAnalyzing] = React.useState(false);
    const [isDarkMode, setIsDarkMode] = React.useState(true);
    const chatEndRef = React.useRef(null);

    React.useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
        if (window.lucide) window.lucide.createIcons();
    }, [messages, isAnalyzing]);

    const analyzeContent = async (text) => {
        setIsAnalyzing(true);
        try {
            const isUrl = text.includes("youtube.com") || text.includes("youtu.be");
            const endpoint = isUrl ? "/verify-url" : "/verify";
            
            const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(isUrl ? { url: text } : { text: text }),
            });

            if (!response.ok) throw new Error("Backend offline");
            const data = await response.json();

            const segments = (data.results || []).map(res => ({
                text: res.sentence,
                status: res.score === 1.0 ? "true" : res.score === 0.0 ? "fake" : "ai",
                color: res.color,    
                reason: res.reason   
            }));

            setMessages(prev => [...prev, {
                role: 'assistant',
                segments: segments.length ? segments : [{ text: text, status: 'ai', color: '#eab308', reason: 'Processing...' }],
                stats: {
                    true: data.summary ? data.summary.score : 0,
                    fake: data.summary ? (100 - data.summary.score) : 0,
                    label: data.summary ? data.summary.label : "Analyzed"
                }
            }]);
        } catch (error) {
            console.error(error);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleSend = (e) => {
        if (e) e.preventDefault();
        if (!inputText.trim()) return;
        setMessages(prev => [...prev, { role: 'user', content: inputText }]);
        analyzeContent(inputText);
        setInputText("");
    };

    return (
        <div className={`flex h-screen w-full transition-all duration-500 ${isDarkMode ? 'bg-[#212121] text-white' : 'bg-white text-black'}`}>
            <aside className={`${isSidebarOpen ? 'w-64' : 'w-0'} bg-[#171717] flex flex-col transition-all border-r border-white/10 text-white overflow-hidden`}>
                <div className="p-4"><button className="flex items-center gap-2 p-2 hover:bg-white/10 rounded-lg w-full text-sm"><Plus /> New Check</button></div>
                <div className="flex-1 px-3 py-2 space-y-1 opacity-80">
                    <p className="text-[10px] font-bold text-gray-500 uppercase px-3 py-2">History</p>
                    <div className="flex items-center gap-3 p-3 rounded-lg text-sm hover:bg-white/5 cursor-pointer"><History size={14}/> Climate News</div>
                </div>
                <div className="p-4 border-t border-white/10"><button onClick={() => setIsDarkMode(!isDarkMode)} className="flex items-center gap-3 w-full p-2 hover:bg-white/5 rounded text-sm"><Settings size={16}/> Dark/Light</button></div>
            </aside>

            <main className="flex-1 flex flex-col relative overflow-hidden">
                <header className="flex flex-col items-center py-4 border-b border-white/5">
                    <h1 className="text-xl font-bold">VERITAS</h1>
                    <p className="text-[9px] uppercase tracking-widest text-gray-500">Authenticity Heatmap v1.0</p>
                </header>

                <div className="flex-1 overflow-y-auto p-4 space-y-6">
                    <div className="max-w-3xl mx-auto">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex gap-4 mb-8 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] ${msg.role === 'user' ? 'bg-[#2f2f2f] rounded-2xl px-4 py-3 text-white' : 'w-full'}`}>
                                    {msg.role === 'assistant' && msg.segments ? (
                                        <div className="space-y-4">
                                            {/* --- HEATMAP DISPLAY START --- */}
                                            <div className="text-[15px] leading-relaxed p-4 bg-white/5 rounded-2xl border border-white/5">
                                                {msg.segments.map((s, i) => (
                                                    <span 
                                                        key={i} 
                                                        title={s.reason} 
                                                        className="px-1 py-0.5 mx-0.5 rounded transition-all cursor-help border-b-2"
                                                        style={{ 
                                                            backgroundColor: `${s.color}20`, 
                                                            borderColor: s.color,            
                                                            color: isDarkMode ? '#fff' : '#000'                  
                                                        }}
                                                    >
                                                        {s.text}
                                                    </span>
                                                ))}
                                            </div>
                                            {/* --- HEATMAP DISPLAY END --- */}
                                            
                                            <div className="grid grid-cols-2 gap-2 p-3 rounded-xl text-center">
                                                <div className="bg-white/5 p-2 rounded-lg"><p className="text-lg font-bold text-green-500">{msg.stats.true}%</p><p className="text-[9px]">TRUSTED</p></div>
                                                <div className="bg-white/5 p-2 rounded-lg"><p className="text-lg font-bold text-red-500">{msg.stats.fake}%</p><p className="text-[9px]">RISK</p></div>
                                            </div>
                                            <div className="text-center text-[10px] font-bold uppercase py-2 bg-white/5 rounded-lg border border-white/10">Verdict: {msg.stats.label}</div>
                                        </div>
                                    ) : <p>{msg.content}</p>}
                                </div>
                            </div>
                        ))}
                        {isAnalyzing && <div className="text-blue-500 animate-pulse text-sm flex items-center gap-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
                            Generating Truth Heatmap...
                        </div>}
                        <div ref={chatEndRef} />
                    </div>
                </div>

                <div className="p-4 pb-8 max-w-3xl mx-auto w-full">
                    <form onSubmit={handleSend} className="relative bg-[#2f2f2f] rounded-3xl p-2 flex items-center shadow-2xl border border-white/5">
                        <textarea value={inputText} onChange={e => setInputText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend(e)} placeholder="Paste content or link here..." className="flex-1 bg-transparent border-none focus:ring-0 text-sm p-3 text-white" rows={1} />
                        <button type="submit" className="p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-full transition-colors"><ArrowUp size={20}/></button>
                    </form>
                </div>
            </main>
        </div>
    );
}

const renderApp = () => {
    const container = document.getElementById('root');
    if (container && !window._veritasRoot) {
        window._veritasRoot = ReactDOM.createRoot(container);
        window._veritasRoot.render(<VersatileApp />);
    }
};

if (document.readyState === 'complete') renderApp();
else window.addEventListener('load', renderApp);