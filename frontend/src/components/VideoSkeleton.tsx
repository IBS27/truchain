export function VideoSkeleton() {
  return (
    <div className="mobile-feed-item relative w-full h-full bg-gray-900 flex items-center justify-center">
      {/* Pulsing background */}
      <div className="absolute inset-0 skeleton-pulse bg-gray-800" />

      {/* Fake action buttons on right */}
      <div className="absolute right-3 bottom-32 flex flex-col items-center gap-5">
        <div className="w-12 h-12 rounded-full bg-gray-700 skeleton-pulse" />
        <div className="w-12 h-12 rounded-full bg-gray-700 skeleton-pulse" />
        <div className="w-12 h-12 rounded-full bg-gray-700 skeleton-pulse" />
      </div>

      {/* Fake bottom info */}
      <div className="absolute bottom-6 left-4 right-20 space-y-3">
        <div className="h-6 w-3/4 bg-gray-700 rounded skeleton-pulse" />
        <div className="h-4 w-1/2 bg-gray-700 rounded skeleton-pulse" />
        <div className="flex gap-3">
          <div className="h-4 w-12 bg-gray-700 rounded skeleton-pulse" />
          <div className="h-4 w-12 bg-gray-700 rounded skeleton-pulse" />
          <div className="h-4 w-12 bg-gray-700 rounded skeleton-pulse" />
        </div>
      </div>

      {/* Center loading indicator */}
      <div className="relative z-10 flex flex-col items-center gap-3">
        <div className="w-16 h-16 rounded-full border-4 border-gray-600 border-t-blue-500 animate-spin" />
        <span className="text-gray-400 text-sm">Loading videos...</span>
      </div>
    </div>
  );
}
