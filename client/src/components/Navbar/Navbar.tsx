const NAME = "Analista de sentencias";

export const Navbar = () => {
  return (
    <nav className="bg-white/70 backdrop-blur-md border-b border-gray-200 shadow-sm fixed top-0 w-full z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo + Nombre */}
        <div className="flex items-center gap-2 min-w-0">
          <img src="/logo.png" alt="logo" className="w-6 h-6 shrink-0" />
          <span className="text-base sm:text-xl font-semibold text-gray-800 truncate">
            {NAME}
          </span>
        </div>

      </div>
    </nav>
  );
};
