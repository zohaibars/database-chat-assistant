from langchain.schema.runnable import(
    RunnableBranch,
    RunnableLambda,
    RunnableMap,
    RunnablePassthrough
)
# branching runnable
branch = RunnableBranch(
    (lambda x: x=="data", "Data Retrieval branch"),
    (lambda x: x=="respond", "Response branch")
)
branch.invoke("data")
