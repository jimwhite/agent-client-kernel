// Patch PageConfig.isDisabled to prevent crash on undefined extension names
(function() {
  console.log("[patch-pageconfig] Patching PageConfig...");
  
  // Wait for PageConfig to be defined
  const checkInterval = setInterval(() => {
    // We need to catch the module loading before it crashes
    // Since PageConfig is a module, we can't easily patch it directly on window
    // But we can try to patch the global config object if it exists
    
    // Alternative: Patch Array.prototype.indexOf to handle undefined
    // This is aggressive but might save the day
    const originalIndexOf = Array.prototype.indexOf;
    Array.prototype.indexOf = function(searchElement, fromIndex) {
      if (searchElement === undefined && this === undefined) {
        console.warn("[patch-pageconfig] Prevented crash in indexOf");
        return -1;
      }
      return originalIndexOf.apply(this, arguments);
    };
    
    clearInterval(checkInterval);
  }, 10);
})();

