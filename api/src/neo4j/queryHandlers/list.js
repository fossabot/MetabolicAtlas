import driver from '../driver.js';

const queryListResult = async (statement) => {
  const session = driver.session();

  let result;
  let error;

  try {
    const response = await session.run(statement);
    result = response.records.map((r) => r.get(0));
  } catch (e) {
    error = e;
  } finally {
    await session.close();
  }

  if (error) {
    throw error;
  }

  return result;
};

export default queryListResult;
