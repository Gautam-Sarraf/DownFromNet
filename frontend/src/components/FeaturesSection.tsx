import React from 'react';
import { 
  Youtube, 
  Facebook, 
  Instagram, 
  Bot, 
  Cloud, 
  Zap, 
  ShieldCheck, 
  Layers, 
  Sparkles,
  Link, 
  Cpu, 
  CheckCircle2, 
  ArrowRight,
  Music,
  Download,
  Share2
} from 'lucide-react';

interface PlatformsSectionProps {
  onSelectSample?: (url: string) => void;
}

const PLATFORM_TILES = [
  {
    name: 'YouTube Downloader',
    icon: Youtube,
    iconColor: 'text-red-600',
    borderColor: 'border-t-red-500',
    description: 'Download videos in multiple formats and resolutions from YouTube.',
    badge: '4K / 1080p / MP3',
    sampleUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
  },
  {
    name: 'Facebook Downloader',
    icon: Facebook,
    iconColor: 'text-blue-600',
    borderColor: 'border-t-blue-500',
    description: 'Save videos and public clips from Facebook with high-quality downloads.',
    badge: 'HD Video',
    sampleUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4'
  },
  {
    name: 'Instagram Downloader',
    icon: Instagram,
    iconColor: 'text-pink-600',
    borderColor: 'border-t-pink-500',
    description: 'Download Instagram reels, posts, image galleries, and clips easily.',
    badge: 'Reels & Photos',
    sampleUrl: 'https://images-assets.nasa.gov/image/PIA12348/PIA12348~orig.jpg'
  },
  {
    name: 'Reddit Downloader',
    icon: Bot,
    iconColor: 'text-orange-500',
    borderColor: 'border-t-orange-500',
    description: 'Download videos with sound and audio tracks from Reddit in HD quality.',
    badge: 'Video & Audio',
    sampleUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'
  },
  {
    name: 'Bluesky Downloader',
    icon: Cloud,
    iconColor: 'text-sky-500',
    borderColor: 'border-t-sky-500',
    description: 'Save videos, GIFs, and media attachments from the Bluesky social network.',
    badge: 'Full Quality',
    sampleUrl: 'https://commons.wikimedia.org/wiki/File:Apollo_11_launch_clip.ogv'
  },
  {
    name: 'TikTok & Short Clips',
    icon: Music,
    iconColor: 'text-slate-900',
    borderColor: 'border-t-slate-800',
    description: 'Extract short videos, sound tracks, and audio streams in seconds.',
    badge: 'No Watermark',
    sampleUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4'
  }
];

const STEPS = [
  {
    step: '1',
    title: 'Copy Video URL',
    description: 'Copy the link of any video, reel, audio, or gallery from your browser or mobile app.'
  },
  {
    step: '2',
    title: 'Paste & Process',
    description: 'Paste the URL in the downloader box above. Our engine instantly analyzes available streams.'
  },
  {
    step: '3',
    title: 'Choose Quality',
    description: 'Select your preferred format (MP4, WebM, MP3) or resolution and save to your device.'
  }
];

const VALUE_PROPS = [
  {
    icon: Zap,
    title: 'High Speed',
    description: 'Multi-threaded stream extraction ensures the fastest possible download speeds.'
  },
  {
    icon: ShieldCheck,
    title: 'Secure & Safe',
    description: 'Zero logging of downloads. Files are sandboxed and automatically cleared after 30 mins.'
  },
  {
    icon: Layers,
    title: 'Multi-Platform',
    description: 'Universal support for video clips, audio tracks, image galleries, and archives.'
  },
  {
    icon: Sparkles,
    title: 'Easy to Use',
    description: 'No apps or browser extensions required. Works seamlessly on desktop and mobile.'
  }
];

export const FeaturesSection: React.FC<PlatformsSectionProps> = ({ onSelectSample }) => {
  return (
    <div className="w-full max-w-5xl mx-auto space-y-16 py-6 sm:py-10">
      {/* 1. Platform Tiles Section (Middle Mockup) */}
      <section id="platforms" className="space-y-6">
        <div className="text-center space-y-1.5">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 font-display">
            Free Online Video Downloader
          </h2>
          <p className="text-sm text-slate-500 max-w-lg mx-auto">
            Extract and download from your favorite platforms with full quality preservation.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {PLATFORM_TILES.map((platform, idx) => {
            const Icon = platform.icon;
            return (
              <div
                key={idx}
                onClick={() => onSelectSample && onSelectSample(platform.sampleUrl)}
                className={`group card-clean card-clean-hover rounded-2xl p-5 border-t-[3px] ${platform.borderColor} flex flex-col justify-between space-y-4 cursor-pointer`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className={`w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center ${platform.iconColor} group-hover:scale-105 transition-transform`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                      {platform.badge}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-slate-900 font-display">
                      {platform.name}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                      {platform.description}
                    </p>
                  </div>
                </div>

                <div className="pt-2 flex items-center gap-1 text-xs font-semibold text-slate-700 group-hover:text-blue-600 transition-colors">
                  <span>Try Downloader</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 2. How To Use Section (Right Mockup) */}
      <section id="how-to-use" className="card-clean rounded-3xl p-6 sm:p-10 space-y-8 bg-white border border-slate-200/80 shadow-soft">
        <div className="text-center space-y-1.5">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
            Simple 3-Step Process
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 font-display">
            How to Use DownFromNet
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            Download your media in 3 simple steps without installing any software.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          {STEPS.map((step, idx) => (
            <div
              key={idx}
              className="bg-slate-50/70 rounded-2xl p-6 border border-slate-200/60 text-center space-y-3 relative group hover:bg-slate-50 transition-colors"
            >
              <div className="w-10 h-10 rounded-full bg-slate-900 text-white font-bold text-sm flex items-center justify-center mx-auto shadow-xs">
                {step.step}
              </div>
              <h3 className="text-base font-bold text-slate-900 font-display">
                {step.title}
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* 3. 4-Value Props Section (Bottom Left Mockup) */}
      <section id="features" className="space-y-6">
        <div className="text-center space-y-1.5">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 font-display">
            Engineered for Clean Simplicity
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto">
            Lightweight, dependable, and privacy-focused universal media extraction.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {VALUE_PROPS.map((prop, idx) => {
            const Icon = prop.icon;
            return (
              <div
                key={idx}
                className="card-clean rounded-2xl p-5 border border-slate-200/80 space-y-3 bg-white"
              >
                <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-800">
                  <Icon className="w-4 h-4 stroke-[2.2]" />
                </div>
                <h3 className="text-sm font-bold text-slate-900 font-display">
                  {prop.title}
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {prop.description}
                </p>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
};
