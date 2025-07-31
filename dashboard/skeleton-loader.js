// Автоматическое подключение skeleton CSS для предотвращения прыгания навигации
(function() {
    // Проверяем, не загружен ли уже skeleton CSS
    if (document.querySelector('link[href*="navigation-skeleton.css"]')) {
        return;
    }
    
    // Создаем и подключаем skeleton CSS
    const skeletonCSS = document.createElement('link');
    skeletonCSS.rel = 'stylesheet';
    skeletonCSS.href = '/dashboard/navigation-skeleton.css';
    
    // Добавляем в head до других стилей навигации
    const navigationCSS = document.querySelector('link[href*="navigation.css"]');
    if (navigationCSS) {
        navigationCSS.parentNode.insertBefore(skeletonCSS, navigationCSS.nextSibling);
    } else {
        document.head.appendChild(skeletonCSS);
    }
    
    console.log('🔮 Skeleton CSS загружен');
})();