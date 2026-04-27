import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [content, setContent] = useState('');
  const [timestamp, setTimestamp] = useState('');
  const [isGlitching, setIsGlitching] = useState(false);
  const [isSealing, setIsSealing] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const timerRef = useRef(null);

  // 动态生成的“考古编码”
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const code = `ARCHIVE_${now.getFullYear()}_${(now.getMonth() + 1).toString().padStart(2, '0')}_${now.getDate()}_T${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`;
      setTimestamp(code);
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  // 处理输入时的 Glitch 效果
  const handleInputChange = (e) => {
    setContent(e.target.value);
    
    // 触发 Glitch 视觉反馈
    setIsGlitching(true);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setIsGlitching(false), 200);
  };

  // 处理封存逻辑
  const handleSave = () => {
    if (!content.trim() || isSealing) return;
    
    setIsSealing(true);
    
    // 模拟封存过程
    setTimeout(() => {
      setIsSealing(false);
      setContent('');
      setShowSuccess(true);
      
      // 成功提示消失后重置
      setTimeout(() => setShowSuccess(false), 2000);
    }, 1200);
  };

  return (
    <>
      {showSuccess && <div className="seal-message">SHARD_SEALED</div>}
      
      <div className={`capsule-container ${isSealing ? 'sealing' : ''}`}>
        {/* 扫描线图层 */}
        <div className="scanlines"></div>

        {/* 头部状态栏 */}
        <div className="header">
          <div className="brand">TYPO_CAPSULE_V1.0</div>
          <div className="id">{timestamp}</div>
        </div>

        {/* 核心输入区 */}
        <div className="input-area">
          <textarea
            className={isGlitching ? 'glitch-text' : ''}
            placeholder="ENTER_DATA_TO_SEAL..."
            value={content}
            onChange={handleInputChange}
            spellCheck="false"
            disabled={isSealing}
          />
        </div>

        {/* 底部操作区 */}
        <div className="footer">
          <div className="status">
            <span className="status-indicator"></span>
            {isSealing ? 'ENCRYPTING_SHARD...' : 'STABLE_VOID_SIGNAL'}
          </div>
          <button 
            className="save-btn" 
            onClick={handleSave}
            disabled={isSealing}
          >
            {isSealing ? 'SEALING...' : 'SEAL_SHARD'}
          </button>
        </div>
      </div>
    </>
  );
}

export default App;
