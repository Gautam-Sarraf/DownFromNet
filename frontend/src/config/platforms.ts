import { 
  Youtube, 
  Facebook, 
  Instagram, 
  Bot, 
  Cloud, 
  Music, 
  Globe,
  Film,
  Zap,
  ShieldCheck,
  Sparkles,
  Layers,
  LucideIcon
} from 'lucide-react';

export interface PlatformConfig {
  id: string;
  slug: string;
  name: string;
  shortName: string;
  icon: LucideIcon;
  iconColor: string;
  badgeColor: string;
  badgeBg: string;
  borderColor: string;
  h1: string;
  badgeText: string;
  subtitle: string;
  metaTitle: string;
  metaDescription: string;
  sampleUrl: string;
  placeholder: string;
  features: { title: string; desc: string; icon: LucideIcon }[];
  howToSteps: { step: string; title: string; desc: string }[];
  faqs: { question: string; answer: string }[];
}

export const PLATFORMS_MAP: Record<string, PlatformConfig> = {
  home: {
    id: 'home',
    slug: '',
    name: 'Universal Video Downloader',
    shortName: 'All Platforms',
    icon: Globe,
    iconColor: 'text-blue-600',
    badgeColor: 'text-blue-700',
    badgeBg: 'bg-blue-50 border-blue-100',
    borderColor: 'border-t-blue-600',
    h1: 'Download any video in high quality.',
    badgeText: 'Internet Utility — Clean & Minimal',
    subtitle: 'The cleanest way to save your favorite content from the web and social platforms. Instant analysis, no ads, high-speed multi-threaded downloads.',
    metaTitle: 'DownFromNet — Free Online Video Downloader (HD, 4K, MP3)',
    metaDescription: 'Download videos from YouTube, Instagram, Facebook, TikTok, Twitter/X, and Reddit in 1080p, 4K, and MP3. Free, fast, and no software required.',
    sampleUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    placeholder: 'Paste any video or media link here...',
    features: [
      { title: 'High-Speed Extraction', desc: 'Multi-threaded stream acquisition ensures fast downloads.', icon: Zap },
      { title: 'Full Quality & 4K', desc: 'Preserves original resolution from 720p and 1080p up to 4K UHD.', icon: Sparkles },
      { title: 'Privacy First', desc: 'Zero logs, no user tracking. Temporary files auto-purged in 30 mins.', icon: ShieldCheck },
      { title: 'All Formats Supported', desc: 'Save as MP4, WebM, MP3 audio, M4A, or full ZIP archives.', icon: Layers }
    ],
    howToSteps: [
      { step: '1', title: 'Copy Video Link', desc: 'Copy the URL of the video or clip from your browser address bar or mobile share menu.' },
      { step: '2', title: 'Paste & Analyze', desc: 'Paste the link into the search box above. Our backend will inspect all available video and audio streams.' },
      { step: '3', title: 'Choose Quality & Save', desc: 'Select your preferred resolution or audio format and click Download to save the media.' }
    ],
    faqs: [
      { question: 'Is DownFromNet completely free to use?', answer: 'Yes! DownFromNet is 100% free with no hidden subscriptions, no ads, and no registration required.' },
      { question: 'Which platforms are supported?', answer: 'You can download videos and audio from YouTube, Facebook, Instagram, TikTok, Twitter / X, Reddit, Vimeo, SoundCloud, and many more.' },
      { question: 'Do I need to install any browser extensions or software?', answer: 'No software or extension installation is needed. DownFromNet runs entirely online in your web browser on desktop, tablet, and mobile.' }
    ]
  },

  youtube: {
    id: 'youtube',
    slug: 'youtube-downloader',
    name: 'YouTube Downloader',
    shortName: 'YouTube',
    icon: Youtube,
    iconColor: 'text-red-600',
    badgeColor: 'text-red-700',
    badgeBg: 'bg-red-50 border-red-200',
    borderColor: 'border-t-red-600',
    h1: 'Download YouTube Videos in 1080p, 4K & MP3',
    badgeText: 'YouTube Video & Audio Downloader',
    subtitle: 'Free and fast YouTube Video Downloader. Save YouTube videos, Shorts, playlists, and audio tracks in crisp 1080p Full HD, 4K UHD, and 320kbps MP3.',
    metaTitle: 'YouTube Video Downloader — Download YouTube Videos in 1080p, 4K & MP3',
    metaDescription: 'Free online YouTube Video Downloader. Download YouTube videos, Shorts, and audio in 1080p, 4K, MP4, and MP3 format at high speed with no watermark or limits.',
    sampleUrl: 'https://youtu.be/dQw4w9WgXcQ',
    placeholder: 'Paste YouTube video, Shorts, or music URL here (e.g. https://youtu.be/...)...',
    features: [
      { title: '4K & 1080p Full HD', desc: 'Download YouTube videos in original 1080p, 1440p, and 4K Ultra HD.', icon: Sparkles },
      { title: 'YouTube Shorts Support', desc: 'Easily download viral YouTube Shorts in portrait MP4 video format.', icon: Film },
      { title: 'Fast MP3 Audio Extraction', desc: 'Convert YouTube music videos to high-bitrate MP3 or M4A audio in seconds.', icon: Music },
      { title: 'No Throttling or Limits', desc: 'Concurrent stream chunking bypasses speed throttling for maximum transfer rate.', icon: Zap }
    ],
    howToSteps: [
      { step: '1', title: 'Copy YouTube URL', desc: 'Open YouTube in your browser or app, find the video or Short, and copy its link.' },
      { step: '2', title: 'Paste in Downloader', desc: 'Paste the YouTube link into the input box above and click Download.' },
      { step: '3', title: 'Select Format & Download', desc: 'Choose between 1080p MP4, 4K UHD, or MP3 audio and save the file directly.' }
    ],
    faqs: [
      { question: 'How do I download YouTube videos in 1080p with audio?', answer: 'DownFromNet automatically fetches separate YouTube video (DASH) and audio streams and merges them with FFmpeg into a complete 1080p MP4 file with crystal-clear sound.' },
      { question: 'Can I download YouTube Shorts with DownFromNet?', answer: 'Yes! Simply paste the YouTube Shorts URL and DownFromNet will download the full vertical video in original HD quality.' },
      { question: 'Can I convert YouTube videos to MP3?', answer: 'Yes! In the format options dropdown, select MP3 Audio or M4A Audio to extract the audio track without downloading unnecessary video data.' }
    ]
  },

  instagram: {
    id: 'instagram',
    slug: 'instagram-downloader',
    name: 'Instagram Downloader',
    shortName: 'Instagram',
    icon: Instagram,
    iconColor: 'text-pink-600',
    badgeColor: 'text-pink-700',
    badgeBg: 'bg-pink-50 border-pink-200',
    borderColor: 'border-t-pink-600',
    h1: 'Download Instagram Videos, Reels & Photos',
    badgeText: 'Instagram Reels & Media Downloader',
    subtitle: 'Save Instagram Reels, videos, carousel posts, stories, and high-resolution photos directly to your device in original quality. 100% free and anonymous.',
    metaTitle: 'Instagram Video Downloader — Download Instagram Reels, Videos & Photos',
    metaDescription: 'Download Instagram Reels, videos, photos, and carousels online in HD quality. Save IGTV and Insta clips directly to your device for free.',
    sampleUrl: 'https://images-assets.nasa.gov/image/PIA12348/PIA12348~orig.jpg',
    placeholder: 'Paste Instagram Reel, Video, or Post URL here (e.g. https://www.instagram.com/reel/...)...',
    features: [
      { title: 'Instagram Reels Downloader', desc: 'Save trending Instagram Reels with full original audio and music.', icon: Film },
      { title: 'Multi-Image Carousel Support', desc: 'Extract all photos and slides from an Instagram carousel post into a single bundle.', icon: Layers },
      { title: 'Original HD Quality', desc: 'Downloads are saved in the highest resolution available without compression.', icon: Sparkles },
      { title: 'No Account or Login Required', desc: 'Download public Instagram content anonymously without logging into your account.', icon: ShieldCheck }
    ],
    howToSteps: [
      { step: '1', title: 'Copy Instagram Post Link', desc: 'On Instagram, tap the Share / Paper Airplane icon on the Reel or Post and select "Copy Link".' },
      { step: '2', title: 'Paste in DownFromNet', desc: 'Paste the Instagram link in the box above and press Download.' },
      { step: '3', title: 'Save Video or Photos', desc: 'Download the Reel as an MP4 or download the photo gallery individually or as a ZIP archive.' }
    ],
    faqs: [
      { question: 'How do I download Instagram Reels with sound?', answer: 'DownFromNet extracts the full media stream including original audio, saving your Reel as a complete MP4 video with sound.' },
      { question: 'Can I download carousel posts with multiple images or videos?', answer: 'Yes! DownFromNet analyzes multi-item carousel posts and lets you download individual items or bundle everything into a ZIP file.' },
      { question: 'Is downloading from Instagram safe and anonymous?', answer: 'Yes, DownFromNet accesses public media streams directly. You never have to share your Instagram credentials or log in.' }
    ]
  },

  facebook: {
    id: 'facebook',
    slug: 'facebook-downloader',
    name: 'Facebook Downloader',
    shortName: 'Facebook',
    icon: Facebook,
    iconColor: 'text-blue-600',
    badgeColor: 'text-blue-700',
    badgeBg: 'bg-blue-50 border-blue-200',
    borderColor: 'border-t-blue-600',
    h1: 'Download Facebook Videos & Reels in HD',
    badgeText: 'Facebook HD Video Downloader',
    subtitle: 'Download public Facebook videos, Facebook Watch streams, and FB Reels in 1080p Full HD MP4 quality. Fast, free, and works on all devices.',
    metaTitle: 'Facebook Video Downloader — Download FB Videos & Reels in HD 1080p',
    metaDescription: 'Free Facebook Video Downloader to save FB videos, Watch clips, and Facebook Reels in Full HD (1080p) MP4 format with audio.',
    sampleUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
    placeholder: 'Paste Facebook video or Reel URL here (e.g. https://fb.watch/... or facebook.com/reel/...)...',
    features: [
      { title: 'Full HD 1080p & SD', desc: 'Choose between high-definition 1080p/720p or data-saving SD formats.', icon: Sparkles },
      { title: 'Facebook Reels Support', desc: 'Download short-form Facebook Reels in universal MP4 format.', icon: Film },
      { title: 'Fast & Direct', desc: 'Instant stream resolution with multi-threaded downloads.', icon: Zap },
      { title: 'Universal Compatibility', desc: 'Works smoothly on Chrome, Safari, Firefox, iPhone, Android, and PC.', icon: Globe }
    ],
    howToSteps: [
      { step: '1', title: 'Copy Facebook Video Link', desc: 'Click the Share button on the Facebook video or Reel and click "Copy Link".' },
      { step: '2', title: 'Paste & Analyze', desc: 'Paste the Facebook link in the search bar above and click Download.' },
      { step: '3', title: 'Save in HD', desc: 'Choose your preferred video quality (1080p HD or 720p) and save the video.' }
    ],
    faqs: [
      { question: 'How do I download Facebook videos in 1080p HD?', answer: 'Paste your Facebook URL into DownFromNet. If the video was uploaded in HD, DownFromNet will display HD format options (1080p/720p) for you to download.' },
      { question: 'Does DownFromNet support Facebook Reels and Watch?', answer: 'Yes! All public Facebook video formats including Watch, Live stream recordings, and Reels are fully supported.' },
      { question: 'Can I download Facebook videos on iPhone or Android?', answer: 'Yes, open DownFromNet in Safari, Chrome, or any mobile browser and paste your FB link to download directly to your camera roll or downloads folder.' }
    ]
  },

  tiktok: {
    id: 'tiktok',
    slug: 'tiktok-downloader',
    name: 'TikTok Downloader',
    shortName: 'TikTok',
    icon: Music,
    iconColor: 'text-slate-900',
    badgeColor: 'text-slate-800',
    badgeBg: 'bg-slate-100 border-slate-200',
    borderColor: 'border-t-slate-900',
    h1: 'Download TikTok Videos Without Watermark',
    badgeText: 'TikTok No-Watermark Downloader',
    subtitle: 'Save TikTok videos in crisp HD MP4 without watermarks, or extract background MP3 sounds and songs with one click. Clean, fast, and free.',
    metaTitle: 'TikTok Video Downloader — Download TikTok Videos Without Watermark',
    metaDescription: 'Download TikTok videos without watermark in HD MP4 or extract MP3 audio. Free online TikTok downloader for mobile and desktop.',
    sampleUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
    placeholder: 'Paste TikTok video link here (e.g. https://www.tiktok.com/@...)...',
    features: [
      { title: 'No Watermark', desc: 'Download clean TikTok videos without the TikTok watermark or username overlay.', icon: Sparkles },
      { title: 'HD Video Quality', desc: 'Extracts the original high-bitrate source video directly from TikTok servers.', icon: Film },
      { title: 'Extract TikTok MP3', desc: 'Convert trending TikTok sounds and voice tracks into standalone MP3 files.', icon: Music },
      { title: 'Fast Mobile Saving', desc: 'Save directly to your iOS or Android camera roll in seconds.', icon: Zap }
    ],
    howToSteps: [
      { step: '1', title: 'Copy TikTok Link', desc: 'Open TikTok, tap the Share arrow on the video, and tap "Copy Link".' },
      { step: '2', title: 'Paste in DownFromNet', desc: 'Paste the TikTok URL in the input box above and press Download.' },
      { step: '3', title: 'Download Without Watermark', desc: 'Select the No-Watermark MP4 option and save the clip to your device.' }
    ],
    faqs: [
      { question: 'How to download TikTok videos without watermark?', answer: 'Paste your TikTok link into DownFromNet. Our engine extracts the clean raw video stream directly from the CDN without the watermark.' },
      { question: 'Can I download only the audio or song from a TikTok video?', answer: 'Yes! Select MP3 Audio in the format dropdown to extract and save the background sound as an audio file.' },
      { question: 'Do I have to pay or create an account to use DownFromNet for TikTok?', answer: 'No, DownFromNet is completely free and requires no account or subscription.' }
    ]
  },

  twitter: {
    id: 'twitter',
    slug: 'twitter-downloader',
    name: 'Twitter / X Downloader',
    shortName: 'Twitter / X',
    icon: Cloud,
    iconColor: 'text-slate-800',
    badgeColor: 'text-slate-800',
    badgeBg: 'bg-slate-100 border-slate-200',
    borderColor: 'border-t-slate-800',
    h1: 'Download Twitter / X Videos & GIFs',
    badgeText: 'Twitter & X Media Downloader',
    subtitle: 'Save high-definition video clips and GIFs from tweets on X (Twitter) in universal MP4 format. Instant stream extraction without limits.',
    metaTitle: 'Twitter Video Downloader — Download X / Twitter Videos & GIFs in HD',
    metaDescription: 'Fast and free Twitter (X) Video Downloader. Download X videos, tweet media clips, and GIFs in MP4 format directly to your device.',
    sampleUrl: 'https://commons.wikimedia.org/wiki/File:Apollo_11_launch_clip.ogv',
    placeholder: 'Paste Twitter / X tweet link here (e.g. https://x.com/... or twitter.com/...)...',
    features: [
      { title: 'Multiple Resolutions', desc: 'Download Twitter videos in 1080p, 720p, 480p, or 360p MP4 formats.', icon: Sparkles },
      { title: 'Twitter GIF to MP4', desc: 'Convert animated Twitter GIFs to lightweight, universal MP4 video files.', icon: Film },
      { title: 'Instant Processing', desc: 'Zero wait times. Direct stream extraction within seconds.', icon: Zap },
      { title: 'Mobile & Desktop Ready', desc: 'Works across iOS, Android, macOS, Windows, and Linux.', icon: Globe }
    ],
    howToSteps: [
      { step: '1', title: 'Copy Tweet Link', desc: 'Click the Share icon at the bottom of the tweet on Twitter/X and select "Copy link to Tweet".' },
      { step: '2', title: 'Paste into DownFromNet', desc: 'Paste the tweet link into the input bar above and click Download.' },
      { step: '3', title: 'Save Video or GIF', desc: 'Pick your desired resolution and download the video to your device.' }
    ],
    faqs: [
      { question: 'How do I download videos from X (Twitter)?', answer: 'Simply copy the link of the tweet containing the video, paste it into DownFromNet, and choose your resolution (1080p/720p/etc.) to save.' },
      { question: 'Can I download Twitter GIFs as video files?', answer: 'Yes! Twitter stores GIFs as MP4 video files. DownFromNet extracts the high-quality MP4 for easy sharing and saving.' },
      { question: 'Is there any limit on how many Twitter videos I can download?', answer: 'No, you can download unlimited Twitter/X videos and GIFs for free.' }
    ]
  },

  reddit: {
    id: 'reddit',
    slug: 'reddit-downloader',
    name: 'Reddit Downloader',
    shortName: 'Reddit',
    icon: Bot,
    iconColor: 'text-orange-600',
    badgeColor: 'text-orange-700',
    badgeBg: 'bg-orange-50 border-orange-200',
    borderColor: 'border-t-orange-600',
    h1: 'Download Reddit Videos with Audio in HD',
    badgeText: 'Reddit Video & Audio Downloader',
    subtitle: 'Download Reddit (v.redd.it) videos with full audio tracks merged in 1080p HD MP4 format. Fast, clean, and reliable extraction.',
    metaTitle: 'Reddit Video Downloader — Download Reddit Videos with Audio in HD',
    metaDescription: 'Download Reddit videos with sound and audio merged in HD 1080p. Free online Reddit video saver for v.redd.it links.',
    sampleUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
    placeholder: 'Paste Reddit post or v.redd.it link here (e.g. https://reddit.com/r/...)...',
    features: [
      { title: 'Video + Audio Merged', desc: 'Reddit stores video and audio separately. We merge them into a single MP4 with sound.', icon: Music },
      { title: '1080p & 720p HD Quality', desc: 'Extracts the highest quality DASH stream available for the post.', icon: Sparkles },
      { title: 'Direct MP4 & MP3', desc: 'Download as complete video or extract standalone audio with sound.', icon: Film },
      { title: 'Multi-threaded Speed', desc: 'Downloads video and audio chunks concurrently for instant merging.', icon: Zap }
    ],
    howToSteps: [
      { step: '1', title: 'Copy Reddit Post URL', desc: 'Click Share on the Reddit post and choose "Copy Link".' },
      { step: '2', title: 'Paste in DownFromNet', desc: 'Paste the Reddit URL into the input field above and click Download.' },
      { step: '3', title: 'Save Merged MP4', desc: 'Click Download to save the complete Reddit video with audio merged.' }
    ],
    faqs: [
      { question: 'Why do Reddit videos downloaded from other websites have no sound?', answer: 'Reddit stores video and audio as separate files (DASH streaming). DownFromNet automatically merges the video and audio tracks with FFmpeg so you get a full video with sound.' },
      { question: 'Can I download Reddit GIFs and videos with sound on iPhone/Android?', answer: 'Yes! DownFromNet merges the streams on our servers and gives you a standard MP4 file ready to play anywhere.' },
      { question: 'Does DownFromNet support all subreddits?', answer: 'Yes, all public subreddits and posts with video or audio attachments are supported.' }
    ]
  }
};

export const PLATFORM_SLUGS: Record<string, string> = {
  '': 'home',
  '/': 'home',
  'youtube': 'youtube',
  'youtube-downloader': 'youtube',
  'instagram': 'instagram',
  'instagram-downloader': 'instagram',
  'facebook': 'facebook',
  'facebook-downloader': 'facebook',
  'tiktok': 'tiktok',
  'tiktok-downloader': 'tiktok',
  'twitter': 'twitter',
  'twitter-downloader': 'twitter',
  'x': 'twitter',
  'reddit': 'reddit',
  'reddit-downloader': 'reddit'
};

export function getPlatformFromPath(path: string): PlatformConfig {
  const cleanPath = path.replace(/^\/+|\/+$/g, '').toLowerCase();
  const platformKey = PLATFORM_SLUGS[cleanPath] || 'home';
  return PLATFORMS_MAP[platformKey] || PLATFORMS_MAP.home;
}
