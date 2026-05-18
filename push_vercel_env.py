import os
import subprocess

def push_env_to_vercel():
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                print(f"Pushing {key} to Vercel production...")
                try:
                    # Execute vercel env add
                    p = subprocess.Popen(
                        ['vercel', 'env', 'add', key, 'production'], 
                        stdin=subprocess.PIPE, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True,
                        shell=True
                    )
                    out, err = p.communicate(input=val + '\n')
                    print(f"Result for {key}: {out.strip()} {err.strip()}")
                except Exception as e:
                    print(f"Error pushing {key}: {e}")
    except Exception as e:
        print(f"Script error: {e}")

if __name__ == '__main__':
    push_env_to_vercel()
