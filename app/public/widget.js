(function() {
  if (window.SupportAIWidgetInitialized) return;
  window.SupportAIWidgetInitialized = true;

  var currentScript = document.currentScript || document.querySelector('script[data-supportai]') || document.getElementById('supportai-widget');
  if (!currentScript) return;

  var config = {
    apiUrl: currentScript.getAttribute('data-api-url') || window.location.origin,
    themeColor: currentScript.getAttribute('data-theme-color') || '#2563EB',
    position: currentScript.getAttribute('data-position') || 'bottom-right',
    greeting: currentScript.getAttribute('data-greeting') || '안녕하세요! 무엇을 도와드릴까요?'
  };

  var isOpen = false;
  var chatSvg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>';
  var closeSvg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';

  var container = document.createElement('div');
  container.id = 'supportai-container';
  var button = document.createElement('button');
  button.id = 'supportai-button';
  button.innerHTML = chatSvg;
  var iframeContainer = document.createElement('div');
  iframeContainer.id = 'supportai-iframe-container';
  var iframe = document.createElement('iframe');
  iframe.id = 'supportai-iframe';
  var widgetUrl = new URL('/widget', config.apiUrl);
  widgetUrl.searchParams.set('embed', 'true');
  widgetUrl.searchParams.set('color', config.themeColor);
  iframe.src = widgetUrl.toString();
  
  var style = document.createElement('style');
  var posCss = config.position === 'bottom-left' ? 'left: 20px;' : 'right: 20px;';
  var originCss = config.position === 'bottom-left' ? 'bottom left' : 'bottom right';
  
  style.textContent = 
    '#supportai-container { position: fixed; bottom: 20px; z-index: 999999; font-family: sans-serif; ' + posCss + ' }' +
    '#supportai-button { width: 56px; height: 56px; border-radius: 50%; background-color: ' + config.themeColor + '; color: white; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: center; transition: transform 0.2s; }' +
    '#supportai-button:hover { transform: scale(1.05); }' +
    '#supportai-button svg { width: 24px; height: 24px; }' +
    '#supportai-iframe-container { position: absolute; bottom: 80px; width: 380px; height: 600px; max-height: calc(100vh - 100px); background: white; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); overflow: hidden; opacity: 0; transform: scale(0.9); transform-origin: ' + originCss + '; transition: opacity 0.3s, transform 0.3s; pointer-events: none; ' + (config.position === 'bottom-left' ? 'left: 0;' : 'right: 0;') + ' }' +
    '#supportai-iframe-container.open { opacity: 1; transform: scale(1); pointer-events: auto; }' +
    '#supportai-iframe { width: 100%; height: 100%; border: none; }' +
    '@media (max-width: 640px) {' +
    '  #supportai-container { bottom: 0; right: 0; left: 0; padding: 16px; display: flex; flex-direction: column; align-items: flex-end; pointer-events: none; }' +
    '  #supportai-button { pointer-events: auto; }' +
    '  #supportai-iframe-container { position: fixed; bottom: 0; left: 0; right: 0; top: 0; width: 100%; height: 100%; max-height: 100%; border-radius: 0; z-index: 1000000; }' +
    '}';

  document.head.appendChild(style);
  
  iframeContainer.appendChild(iframe);
  container.appendChild(iframeContainer);
  container.appendChild(button);
  document.body.appendChild(container);

  function toggleWidget() {
    isOpen = !isOpen;
    if (isOpen) {
      iframeContainer.classList.add('open');
      button.innerHTML = closeSvg;
    } else {
      iframeContainer.classList.remove('open');
      button.innerHTML = chatSvg;
    }
  }

  button.addEventListener('click', toggleWidget);

  window.addEventListener('message', function(event) {
    if (event.origin !== new URL(config.apiUrl).origin) return;
    
    if (event.data.type === 'supportai:close') {
      if (isOpen) toggleWidget();
    }
  });

  window.SupportAIWidget = {
    toggle: toggleWidget,
    open: function() { if (!isOpen) toggleWidget(); },
    close: function() { if (isOpen) toggleWidget(); },
    config: config
  };

})();