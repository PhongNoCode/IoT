"""
Replay Attack Tool
Tool for replaying captured RFID/NFC commands
"""

from datetime import datetime


class ReplayAttack:
    """Replay attack tool"""
    
    def __init__(self):
        """Initialize replay attack tool"""
        self.captured_frames = []
        self.replay_count = 0
    
    def capture_frame(self, frame_data: dict):
        """
        Capture a frame for later replay
        
        Args:
            frame_data: Frame data to capture
        """
        self.captured_frames.append(frame_data)
        print(f"[+] Frame captured for replay: {frame_data}")
    
    def replay_frame(self, frame_index: int) -> dict:
        """
        Replay a captured frame
        
        Args:
            frame_index: Index of frame to replay
            
        Returns:
            Replayed frame data
        """
        if 0 <= frame_index < len(self.captured_frames):
            frame = self.captured_frames[frame_index].copy()
            frame["replayed_at"] = datetime.now().isoformat()
            self.replay_count += 1
            print(f"[+] Frame replayed: {frame}")
            return frame
        return None
    
    def replay_all_frames(self) -> list:
        """Replay all captured frames"""
        replayed = []
        for i in range(len(self.captured_frames)):
            replayed.append(self.replay_frame(i))
        return replayed
    
    def get_replay_count(self) -> int:
        """Get total number of replays"""
        return self.replay_count


if __name__ == "__main__":
    replay = ReplayAttack()
    
    replay.capture_frame({"uid": "04F3B2A1C5", "command": "READ"})
    replay.capture_frame({"uid": "04F3B2A1C5", "command": "AUTHENTICATE"})
    
    replay.replay_frame(0)
    print(f"Total replays: {replay.get_replay_count()}")
