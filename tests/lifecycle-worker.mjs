// Bounded fixture, only started by process-lifecycle-test.ps1.
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
if (process.argv[2] === 'idle') setTimeout(() => {}, 120_000);
else {
  spawn(process.execPath, [import.meta.filename, 'idle'], {windowsHide: true, stdio: 'ignore'});
  const server = createServer((request, response) => {
    response.setHeader('Content-Type', 'application/json');
    response.end(JSON.stringify({fixture: 'sunny-lifecycle', ready: true}));
  });
  setTimeout(() => server.listen(Number(process.argv[2]), '127.0.0.1'), Number(process.argv[3] ?? 0));
  setTimeout(() => server.close(() => process.exit()), 120_000).unref();
}
