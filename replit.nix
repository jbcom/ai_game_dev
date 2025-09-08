{ pkgs }: {
  deps = [
    # Development tools
    pkgs.just
    pkgs.imagemagick
    
    # Python build dependencies
    pkgs.gcc
    pkgs.gnumake
    
    # Audio/Video processing (for asset generation)
    pkgs.ffmpeg
    
    # Git for version control
    pkgs.git
    
    # Process management
    pkgs.tmux
    
    # Optional: Node.js for custom frontend development
    pkgs.nodejs_20
    pkgs.nodePackages.npm
  ];
}