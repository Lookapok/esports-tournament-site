// 頁面性能優化和互動功能 v2.0
document.addEventListener('DOMContentLoaded', function() {
    // ===== 頁面載入性能優化 =====
    
    // 延遲載入非關鍵圖片
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    }
    
    // ===== 頁面切換加速 =====
    
    // 預載入連結
    const links = document.querySelectorAll('a[href^="/"]');
    links.forEach(link => {
        link.addEventListener('mouseenter', function() {
            if (!this.dataset.prefetched) {
                const prefetchLink = document.createElement('link');
                prefetchLink.rel = 'prefetch';
                prefetchLink.href = this.href;
                document.head.appendChild(prefetchLink);
                this.dataset.prefetched = 'true';
            }
        });
    });
    
    // ===== 原有功能保持 =====
    
    // 對戰圖表高亮功能
    const winners = document.querySelectorAll('.participant.winner');

    winners.forEach(winnerNode => {
        winnerNode.addEventListener('click', function() {
            // 移除舊的高亮
            document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
            document.querySelectorAll('.highlight-line').forEach(el => el.classList.remove('highlight-line'));

            const teamId = winnerNode.dataset.teamId;

            // 找到所有屬於該隊伍的參賽者元素
            const teamParticipants = document.querySelectorAll(`.participant[data-team-id="${teamId}"]`);

            teamParticipants.forEach(p => {
                // 為隊伍本身加上高亮
                p.classList.add('highlight');

                // 找到它所屬的比賽容器 (match-up)，並為連接線也加上高亮 class
                const matchUp = p.closest('.match-up');
                if (matchUp) {
                    matchUp.classList.add('highlight-line');
                }
            });
        });
    });
});

// --- 歷史戰績展開/收合功能 ---
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggle-matches-btn');
    const matchContainer = document.getElementById('match-history-container');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            const hiddenMatches = matchContainer.querySelectorAll('.is_hidden');
            
            // 檢查是否所有都已顯示，決定是隱藏還是顯示
            let allVisible = true;
            hiddenMatches.forEach(match => {
                if (match.style.display === 'none' || match.style.display === '') {
                    allVisible = false;
                }
            });

            hiddenMatches.forEach(match => {
                if (allVisible) {
                    match.style.display = 'none'; // 隱藏
                } else {
                    match.style.display = 'flex'; // 顯示 (使用 flex 讓內部元素水平排列)
                }
            });

            if (allVisible) {
                toggleBtn.textContent = '顯示更多紀錄';
            } else {
                toggleBtn.textContent = '收合紀錄';
            }
        });
    }
});