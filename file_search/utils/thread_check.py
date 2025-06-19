import threading

def print_active_threads():
    """
    Prints the status of all active threads that are not properly closed.
    This helps identify threads that may prevent clean application shutdown.
    """
    active_threads = threading.enumerate()
    main_thread = threading.main_thread()
    
    print("\n=== Thread Status Report ===")
    print(f"Total active threads: {len(active_threads)}")
    print(f"Main thread: {main_thread.name} (ID: {main_thread.ident})")
    
    # Filter out the main thread to focus on potentially problematic threads
    non_main_threads = [t for t in active_threads if t != main_thread]
    
    if not non_main_threads:
        print("✅ All non-main threads have been properly closed.")
        return
    
    print(f"\n⚠️  Found {len(non_main_threads)} active non-main thread(s):")
    print("-" * 60)
    
    for i, thread in enumerate(non_main_threads, 1):
        print(f"{i}. Thread Name: {thread.name}")
        print(f"   Thread ID: {thread.ident}")
        print(f"   Is Alive: {thread.is_alive()}")
        print(f"   Is Daemon: {thread.daemon}")
        print(f"   Thread Class: {thread.__class__.__name__}")
        
        # Check if it's a daemon thread (these usually don't prevent shutdown)
        if thread.daemon:
            print("   Status: 🟡 Daemon thread (won't block shutdown)")
        else:
            print("   Status: 🔴 Non-daemon thread (may block shutdown)")
        
        print()