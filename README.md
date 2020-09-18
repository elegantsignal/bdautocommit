# bdautocommit - simple example how to create `@transactional` decorator for aiopg.

Project demonstrates how from this:

```python
async def save(account):
    async with engine.acquire() as connection:
        async with connection.begin():
            await repository.save(connection, account)
```

make this:

```python
@transactional
async def save(connection, account):
    await repository.save(connection, account)
```


In both case call looks:

```python
account=Account(...)
save(account)
```
