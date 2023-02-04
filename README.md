# self_governance
Self-governing nations on https://www.nationstates.net/

## How it works

self_governance uses [OpenAI text
completion](https://platform.openai.com/docs/guides/completion) to automatically
answer issues based on a description of a nation.

## Usage

Invoke the module with the name and a short description of your nation:

```
# the following commands are prefixed with a space to prevent them from being
# saved in shell history
 export NATIONSTATES_PASSWORD=xxx
 export OPENAI_API_KEY=yyy
python -m self_governance Wilbert 'Wilbert is a nation which values conformity, efficiency and economic growth.'
```
