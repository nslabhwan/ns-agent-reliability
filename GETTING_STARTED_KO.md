# OpenSynapse 한국어 시작 안내

**AI가 알려준 명령을 매번 복사하지 않고, 연결한 작업 폴더에서 파일 읽기·쓰기와 허용한 명령을 직접 실행하도록 하는 오픈소스입니다.**

NS에서 운영하며 만든 실행 기능을 공개한 프로젝트입니다. Linux와 Android/Termux를 지원합니다. 처음에는 아래 로컬 데모로 실제 파일이 만들어지는지 확인하세요.

## 1. 먼저 내 환경 확인하기

- Linux: Python 3.11 이상과 Git이 필요합니다.
- Android: Termux 안에서 실행합니다. 필요한 Python과 Git은 설치 스크립트가 설치할 수 있습니다.
- Windows와 macOS 전용 패키지는 아직 제공하지 않습니다.
- 아래 데모는 로컬 실행입니다. ChatGPT 연결은 별도 설정입니다.

## 2. 설치하고 첫 파일 만들기

[실행할 스크립트](https://github.com/nslabhwan/ns-agent-reliability/blob/main/try.sh)를 확인한 뒤, Linux 또는 Termux 터미널에서 실행하세요.

```bash
curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/try.sh | bash
```

스크립트는 전용 작업 폴더를 만들고 OpenSynapse를 설치한 다음, 접근 범위를 점검하고 파일 생성·읽기를 실행합니다.

완료되면 다음 파일이 남습니다.

```text
~/OpenSynapseWorkspace/OPENSYNAPSE_DEMO.txt
```

직접 확인하려면:

```bash
cat "$HOME/OpenSynapseWorkspace/OPENSYNAPSE_DEMO.txt"
```

이 파일을 확인하면 첫 로컬 실행이 끝난 것입니다. 설치 시간은 기기와 네트워크에 따라 다릅니다.

## 3. AI와 연결해서 쓰기

로컬 MCP 클라이언트를 사용한다면 다음 명령으로 서버를 실행합니다.

```bash
opensynapse serve --transport stdio
```

ChatGPT 연결 방법: [기존 연결 안내](GETTING_STARTED.md#c-connect-a-private-node-through-openai-secure-mcp-tunnel). 계정에서 제공되는 연결 기능과 별도 설정이 필요하며, 위 데모 명령만으로 ChatGPT 연결까지 완료되지는 않습니다.

연결한 뒤 첫 작업은 이렇게 요청할 수 있습니다.

> 허용된 작업 폴더를 확인하고 hello.txt에 '첫 작업 완료'를 저장해줘. 저장한 파일을 다시 읽어서 내용도 확인해줘.

명령 실행은 미리 허용한 범위에서만 가능합니다. 기본 설정은 기기 전체를 자유롭게 조작하는 방식이 아닙니다.

## 4. 현재 공개된 검증 범위

- Linux에서 설치, 파일 읽기·쓰기, 제한된 명령 실행 경로를 검증했습니다.
- 실제 Android/Termux 기기에서 설치와 로컬 MCP 파일 읽기·쓰기를 검증했습니다.
- Linux의 실제 ChatGPT 연결을 통한 파일 생성·다시 읽기: [공개 실행 기록](docs/REAL_CHATGPT_E2E_20260920.md).
- Android를 ChatGPT에서 원격으로 제어하는 전체 연결은 아직 검증 완료로 안내하지 않습니다.

공개 기능과 내부 NS 시스템 전체는 동일하지 않습니다. 현재 배포 범위: [영문 시작 안내](GETTING_STARTED.md), [저장소](README.md).

## 5. 막힌 부분을 한국어로 남기기

별도 영문 문의를 만들 필요 없이 한국어로 남겨주세요.

- [기존 Discord 커뮤니티](https://discord.gg/YBKQpC6aem)
- [GitHub 사용 기록·문제 접수](https://github.com/nslabhwan/ns-agent-reliability/issues/new?template=opensynapse-feedback.yml)

사용 환경, 마지막으로 성공한 단계, 오류 메시지, 하려던 작업을 적어주면 됩니다. 비밀번호·API 키·개인 자료는 올리지 마세요.

`opensynapse: command not found`가 나오면 다음 경로로 확인하세요.

```bash
"$HOME/.local/bin/opensynapse" doctor
```

읽기는 되는데 쓰기가 안 된다면 `opensynapse status`에서 쓰기 허용 폴더를 확인하세요. [접근 범위와 보안 안내](SECURITY.md)도 함께 제공하고 있습니다.

## 라이선스

소프트웨어는 Apache-2.0 라이선스로 공개되어 있습니다. 호스팅 환경과 연결하는 외부 서비스의 이용 조건·비용은 별도입니다.
